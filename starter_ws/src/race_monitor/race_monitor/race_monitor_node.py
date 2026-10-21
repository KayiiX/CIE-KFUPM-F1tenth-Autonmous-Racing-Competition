"""Publish competition-friendly lap timing derived from the simulator."""

import math

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Bool, Float32, Float32MultiArray, Int32, String


class RaceMonitor(Node):
    """Combine official completed-lap data with a live Levine stopwatch."""

    def __init__(self):
        super().__init__("race_monitor")

        self.declare_parameter("odom_topic", "/ego_racecar/odom")
        self.declare_parameter(
            "official_lap_count_topic", "/ego_racecar/lap_count"
        )
        self.declare_parameter(
            "official_lap_time_topic", "/ego_racecar/lap_time"
        )
        self.declare_parameter(
            "collision_topic", "/ego_racecar/collision"
        )
        self.declare_parameter("finish_x", 0.0310)
        self.declare_parameter("finish_y", -0.0691)
        self.declare_parameter("finish_tangent_x", 1.0)
        self.declare_parameter("finish_tangent_y", 0.0)
        self.declare_parameter("finish_half_width", 1.0)
        self.declare_parameter("finish_approach_distance", 2.0)
        self.declare_parameter("finish_rearm_distance", 0.5)

        self.finish_x = float(self.get_parameter("finish_x").value)
        self.finish_y = float(self.get_parameter("finish_y").value)
        tx = float(self.get_parameter("finish_tangent_x").value)
        ty = float(self.get_parameter("finish_tangent_y").value)
        tangent_norm = math.hypot(tx, ty)
        if tangent_norm == 0.0:
            raise ValueError("finish-line tangent cannot be zero")
        self.tangent_x = tx / tangent_norm
        self.tangent_y = ty / tangent_norm
        self.normal_x = -self.tangent_y
        self.normal_y = self.tangent_x
        self.finish_half_width = float(
            self.get_parameter("finish_half_width").value
        )
        self.approach_distance = float(
            self.get_parameter("finish_approach_distance").value
        )
        self.rearm_distance = float(
            self.get_parameter("finish_rearm_distance").value
        )

        self.lap_count = 0
        self.last_lap_time = 0.0
        self.best_lap_time = 0.0
        self.lap_history = []
        self.latest_official_lap_time = 0.0
        self.pending_lap_count = None
        self.pending_deadline_ns = None
        self.collision_count = 0
        self.collision_active = False

        self.status = "WAITING_FOR_ODOMETRY"
        self.previous_longitudinal = None
        self.finish_armed = False
        self.lap_start_ns = None
        self.paused = False
        self.pause_started_ns = None
        self.paused_duration_ns = 0

        self.current_pub = self.create_publisher(
            Float32, "/competition/current_lap_time", 10
        )
        self.last_pub = self.create_publisher(
            Float32, "/competition/last_lap_time", 10
        )
        self.best_pub = self.create_publisher(
            Float32, "/competition/best_lap_time", 10
        )
        self.count_pub = self.create_publisher(
            Int32, "/competition/lap_count", 10
        )
        self.status_pub = self.create_publisher(
            String, "/competition/race_status", 10
        )
        self.history_pub = self.create_publisher(
            Float32MultiArray, "/competition/lap_history", 10
        )
        self.collision_count_pub = self.create_publisher(
            Int32, "/competition/collision_count", 10
        )

        self.create_subscription(
            Odometry,
            str(self.get_parameter("odom_topic").value),
            self.odom_callback,
            20,
        )
        self.create_subscription(
            Int32,
            str(self.get_parameter("official_lap_count_topic").value),
            self.lap_count_callback,
            20,
        )
        self.create_subscription(
            Float32,
            str(self.get_parameter("official_lap_time_topic").value),
            self.lap_time_callback,
            20,
        )
        self.create_subscription(
            Bool,
            str(self.get_parameter("collision_topic").value),
            self.collision_callback,
            20,
        )
        self.create_subscription(Bool, "/pause_sim", self.pause_callback, 10)
        self.create_subscription(
            PoseWithCovarianceStamped,
            "/initialpose",
            self.reset_callback,
            10,
        )

        self.create_timer(0.1, self.publish_state)
        self.get_logger().info(
            "Race monitor ready. The first finish-line crossing ends the out-lap."
        )

    def now_ns(self):
        return self.get_clock().now().nanoseconds

    def reset_session(self):
        """Clear session timing after a simulator pose reset."""
        self.lap_count = 0
        self.last_lap_time = 0.0
        self.best_lap_time = 0.0
        self.lap_history = []
        self.latest_official_lap_time = 0.0
        self.pending_lap_count = None
        self.pending_deadline_ns = None
        self.collision_count = 0
        self.collision_active = False
        self.status = "OUT_LAP"
        self.previous_longitudinal = None
        self.finish_armed = False
        self.lap_start_ns = None
        self.pause_started_ns = None
        self.paused_duration_ns = 0
        self.get_logger().info("Race timing reset; waiting for the finish line.")

    def reset_callback(self, _msg):
        self.reset_session()

    def pause_callback(self, msg):
        now = self.now_ns()
        if msg.data and not self.paused:
            self.paused = True
            self.pause_started_ns = now
        elif not msg.data and self.paused:
            if self.pause_started_ns is not None and self.lap_start_ns is not None:
                self.paused_duration_ns += now - self.pause_started_ns
            self.paused = False
            self.pause_started_ns = None

    def finish_coordinates(self, x, y):
        """Return along-track and across-track coordinates at the finish line."""
        dx = x - self.finish_x
        dy = y - self.finish_y
        longitudinal = dx * self.tangent_x + dy * self.tangent_y
        lateral = dx * self.normal_x + dy * self.normal_y
        return longitudinal, lateral

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        longitudinal, lateral = self.finish_coordinates(x, y)

        if self.status == "WAITING_FOR_ODOMETRY":
            self.status = "OUT_LAP"

        inside_gate = abs(lateral) <= self.finish_half_width
        if (
            inside_gate
            and -self.approach_distance <= longitudinal <= -self.rearm_distance
        ):
            self.finish_armed = True

        crossed_forward = (
            self.finish_armed
            and inside_gate
            and self.previous_longitudinal is not None
            and self.previous_longitudinal < 0.0 <= longitudinal
        )
        if crossed_forward:
            now = self.now_ns()
            if self.lap_start_ns is None:
                self.get_logger().info("Out-lap complete; live lap timer started.")
            self.lap_start_ns = now
            self.paused_duration_ns = 0
            if self.paused:
                self.pause_started_ns = now
            self.status = "RACING"
            self.finish_armed = False

        if longitudinal > self.rearm_distance:
            self.finish_armed = False
        self.previous_longitudinal = longitudinal

    def lap_count_callback(self, msg):
        official_count = int(msg.data)
        if official_count < self.lap_count:
            self.reset_session()
        if official_count > self.lap_count:
            self.lap_count = official_count
            self.pending_lap_count = official_count
            self.pending_deadline_ns = self.now_ns() + 50_000_000
        else:
            self.lap_count = official_count

    def lap_time_callback(self, msg):
        self.latest_official_lap_time = float(msg.data)

    def collision_callback(self, msg):
        collision_now = bool(msg.data)
        if collision_now and not self.collision_active:
            self.collision_count += 1
            self.get_logger().warning(
                f"Collision {self.collision_count} recorded."
            )
        self.collision_active = collision_now

    def finalize_pending_lap(self):
        if self.pending_lap_count is None:
            return
        lap_time = self.latest_official_lap_time
        if lap_time > 0.0:
            self.last_lap_time = lap_time
            self.lap_history.append(lap_time)
            if self.best_lap_time == 0.0 or lap_time < self.best_lap_time:
                self.best_lap_time = lap_time
            self.get_logger().info(
                f"Lap {self.pending_lap_count}: {lap_time:.3f} s "
                f"(best {self.best_lap_time:.3f} s)"
            )
        self.pending_lap_count = None
        self.pending_deadline_ns = None

    def current_lap_time(self, now):
        if self.lap_start_ns is None:
            return 0.0
        end = now
        if self.paused and self.pause_started_ns is not None:
            end = self.pause_started_ns
        elapsed = end - self.lap_start_ns - self.paused_duration_ns
        return max(0.0, elapsed / 1_000_000_000.0)

    def publish_state(self):
        now = self.now_ns()
        if (
            self.pending_deadline_ns is not None
            and now >= self.pending_deadline_ns
        ):
            self.finalize_pending_lap()

        current = self.current_lap_time(now)
        self.current_pub.publish(Float32(data=current))
        self.last_pub.publish(Float32(data=self.last_lap_time))
        self.best_pub.publish(Float32(data=self.best_lap_time))
        self.count_pub.publish(Int32(data=self.lap_count))
        self.status_pub.publish(String(data=self.status))
        self.history_pub.publish(Float32MultiArray(data=self.lap_history))
        self.collision_count_pub.publish(Int32(data=self.collision_count))


def main(args=None):
    rclpy.init(args=args)
    node = RaceMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()

"""Convert a standardized PS5 Joy message into safe Ackermann commands."""

import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.node import Node
from sensor_msgs.msg import Joy


def clamp(value, minimum, maximum):
    """Clamp value to an inclusive range."""
    return max(minimum, min(maximum, value))


class Ps5Teleop(Node):
    """PS5 teleoperation with a hold-to-drive enable button and timeout."""

    def __init__(self):
        super().__init__("ps5_teleop")

        self.declare_parameter("joy_topic", "/joy")
        self.declare_parameter("drive_topic", "/drive")
        self.declare_parameter("steering_axis", 0)
        self.declare_parameter("reverse_axis", 4)
        self.declare_parameter("throttle_axis", 5)
        self.declare_parameter("stop_button", 0)
        self.declare_parameter("enable_button", 9)
        self.declare_parameter("maximum_forward_speed", 1.5)
        self.declare_parameter("maximum_reverse_speed", 0.5)
        self.declare_parameter("maximum_steering_angle", 0.35)
        self.declare_parameter("trigger_deadzone", 0.05)
        self.declare_parameter("joy_timeout", 0.5)

        self.steering_axis = int(self.get_parameter("steering_axis").value)
        self.reverse_axis = int(self.get_parameter("reverse_axis").value)
        self.throttle_axis = int(self.get_parameter("throttle_axis").value)
        self.stop_button = int(self.get_parameter("stop_button").value)
        self.enable_button = int(self.get_parameter("enable_button").value)
        self.maximum_forward_speed = float(
            self.get_parameter("maximum_forward_speed").value
        )
        self.maximum_reverse_speed = float(
            self.get_parameter("maximum_reverse_speed").value
        )
        self.maximum_steering_angle = float(
            self.get_parameter("maximum_steering_angle").value
        )
        self.trigger_deadzone = float(
            self.get_parameter("trigger_deadzone").value
        )
        self.joy_timeout_ns = int(
            float(self.get_parameter("joy_timeout").value) * 1_000_000_000
        )

        drive_topic = str(self.get_parameter("drive_topic").value)
        joy_topic = str(self.get_parameter("joy_topic").value)
        self.drive_pub = self.create_publisher(
            AckermannDriveStamped, drive_topic, 10
        )
        self.joy_sub = self.create_subscription(
            Joy, joy_topic, self.joy_callback, 20
        )
        self.last_joy_ns = None
        self.timeout_stop_sent = False
        self.invalid_layout_reported = False
        self.create_timer(0.05, self.watchdog_callback)

        self.get_logger().info(
            "PS5 teleop ready: hold L1, steer with left stick, "
            "R2 forward, L2 reverse, Cross stop."
        )

    def publish_drive(self, speed, steering):
        message = AckermannDriveStamped()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "ego_racecar/base_link"
        message.drive.speed = float(speed)
        message.drive.steering_angle = float(steering)
        self.drive_pub.publish(message)

    def layout_is_valid(self, message):
        required_axis = max(
            self.steering_axis, self.reverse_axis, self.throttle_axis
        )
        required_button = max(self.stop_button, self.enable_button)
        valid = (
            len(message.axes) > required_axis
            and len(message.buttons) > required_button
        )
        if not valid and not self.invalid_layout_reported:
            self.get_logger().error(
                "Controller layout is too short for the configured PS5 mapping."
            )
            self.invalid_layout_reported = True
        return valid

    def trigger_value(self, axis_value):
        # game_controller_node inverts SDL axes: unpressed is 0, pressed is -1.
        value = clamp(-float(axis_value), 0.0, 1.0)
        if value <= self.trigger_deadzone:
            return 0.0
        return (value - self.trigger_deadzone) / (1.0 - self.trigger_deadzone)

    def joy_callback(self, message):
        self.last_joy_ns = self.get_clock().now().nanoseconds
        self.timeout_stop_sent = False
        if not self.layout_is_valid(message):
            self.publish_drive(0.0, 0.0)
            return

        enabled = bool(message.buttons[self.enable_button])
        stop_pressed = bool(message.buttons[self.stop_button])
        if not enabled or stop_pressed:
            self.publish_drive(0.0, 0.0)
            return

        throttle = self.trigger_value(message.axes[self.throttle_axis])
        reverse = self.trigger_value(message.axes[self.reverse_axis])
        if throttle > 0.0 and reverse > 0.0:
            speed = 0.0
        else:
            speed = (
                throttle * self.maximum_forward_speed
                - reverse * self.maximum_reverse_speed
            )

        steering = clamp(
            float(message.axes[self.steering_axis]), -1.0, 1.0
        ) * self.maximum_steering_angle
        self.publish_drive(speed, steering)

    def watchdog_callback(self):
        if self.last_joy_ns is None or self.timeout_stop_sent:
            return
        elapsed = self.get_clock().now().nanoseconds - self.last_joy_ns
        if elapsed > self.joy_timeout_ns:
            self.publish_drive(0.0, 0.0)
            self.timeout_stop_sent = True
            self.get_logger().warning(
                "Controller messages timed out; a stop command was sent."
            )


def main(args=None):
    rclpy.init(args=args)
    node = Ps5Teleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_drive(0.0, 0.0)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
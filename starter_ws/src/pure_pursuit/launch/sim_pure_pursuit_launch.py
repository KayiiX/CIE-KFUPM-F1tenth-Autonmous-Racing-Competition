from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    package_share = get_package_share_directory("pure_pursuit")
    config = os.path.join(package_share, "config", "sim_config.yaml")
    waypoints = os.path.join(
        package_share, "racelines", "levine_centerline_pp.csv"
    )

    return LaunchDescription([
        Node(
            package="pure_pursuit",
            executable="pure_pursuit",
            name="pure_pursuit",
            parameters=[config, {"waypoints_path": waypoints}],
            output="screen",
        ),
        Node(
            package="pure_pursuit",
            executable="waypoint_visualizer",
            name="waypoint_visualizer_node",
            parameters=[config, {"waypoints_path": waypoints}],
            output="screen",
        ),
    ])


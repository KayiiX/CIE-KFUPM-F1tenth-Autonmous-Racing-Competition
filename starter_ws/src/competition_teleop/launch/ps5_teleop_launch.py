import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory("competition_teleop"),
        "config",
        "ps5.yaml",
    )

    controller = Node(
        package="joy",
        executable="game_controller_node",
        name="game_controller_node",
        parameters=[config],
        output="screen",
    )

    teleop = Node(
        package="competition_teleop",
        executable="ps5_teleop",
        name="ps5_teleop",
        parameters=[config],
        output="screen",
    )

    return LaunchDescription([controller, teleop])
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    simulator_share = get_package_share_directory("f1tenth_gym_ros")

    simulator = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(simulator_share, "launch", "gym_bridge_launch.py")
        ),
        launch_arguments={
            "num_agents": "1",
            "open_foxglove": "false",
        }.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=[
            "-d",
            os.path.join(
                simulator_share,
                "config",
                "rviz",
                "gym_bridge.rviz",
            ),
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            simulator,
            rviz,
        ]
    )

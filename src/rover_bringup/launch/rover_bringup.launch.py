"""Installable bringup for Axiom Rover Mulo.

Usage:
  ros2 launch rover_bringup rover_bringup.launch.py profile:=sim
  ros2 launch rover_bringup rover_bringup.launch.py profile:=bench nav:=false
  ros2 launch rover_bringup rover_bringup.launch.py profile:=production
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _bool_arg(context, name: str) -> bool:
    return LaunchConfiguration(name).perform(context).lower() in ("1", "true", "yes", "on")


def _launch_nodes(context):
    profile = LaunchConfiguration("profile").perform(context)
    params_file = LaunchConfiguration("params_file").perform(context)
    bringup_share = get_package_share_directory("rover_bringup")
    profile_file = os.path.join(bringup_share, "config", "profiles", f"{profile}.yaml")
    if not os.path.exists(profile_file):
        raise RuntimeError(f"Unknown rover bringup profile '{profile}': {profile_file}")

    parameters = [params_file, profile_file]
    description_share = get_package_share_directory("rover_description")
    urdf_path = os.path.join(description_share, "urdf", "axiom_rover.urdf")
    robot_description = {}
    if os.path.exists(urdf_path):
        with open(urdf_path, encoding="utf-8") as urdf_file:
            robot_description = {"robot_description": urdf_file.read()}

    actions = [
        LogInfo(msg=f"[BRINGUP] profile={profile} params={params_file} profile_file={profile_file}"),
        Node(
            package="rover_system",
            executable="hardware_bridge",
            name="hardware_bridge",
            output="screen",
            parameters=parameters,
            respawn=True,
            respawn_delay=1.0,
        ),
        TimerAction(
            period=0.3,
            actions=[
                Node(
                    package="rover_safety",
                    executable="safety_watchdog",
                    name="safety_watchdog",
                    output="screen",
                    parameters=parameters,
                    respawn=True,
                    respawn_delay=1.0,
                )
            ],
        ),
        TimerAction(
            period=0.5,
            actions=[
                Node(
                    package="rover_safety",
                    executable="stability_margin",
                    name="stability_margin",
                    output="screen",
                    parameters=parameters,
                    respawn=True,
                    respawn_delay=1.0,
                )
            ],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[robot_description] if robot_description else [],
        ),
        TimerAction(
            period=1.0,
            actions=[
                Node(
                    package="rover_control",
                    executable="vesc_driver",
                    name="vesc_driver",
                    output="screen",
                    parameters=parameters,
                    respawn=True,
                    respawn_delay=2.0,
                )
            ],
        ),
        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package="rover_power",
                    executable="power_monitor",
                    name="power_monitor",
                    output="screen",
                    parameters=parameters,
                    respawn=True,
                    respawn_delay=2.0,
                )
            ],
        ),
        TimerAction(
            period=2.8,
            actions=[
                Node(
                    package="rover_system",
                    executable="state_estimation",
                    name="state_estimation",
                    output="screen",
                    parameters=parameters,
                    respawn=True,
                    respawn_delay=2.0,
                )
            ],
        ),
    ]

    if _bool_arg(context, "winch"):
        actions.append(
            TimerAction(
                period=2.0,
                actions=[
                    Node(
                        package="rover_winch",
                        executable="winch_manager",
                        name="winch_manager",
                        output="screen",
                        parameters=parameters,
                        respawn=True,
                        respawn_delay=2.0,
                    )
                ],
            )
        )
    if _bool_arg(context, "terrain"):
        actions.append(
            TimerAction(
                period=2.5,
                actions=[
                    Node(
                        package="rover_navigation",
                        executable="terrain_assessor",
                        name="terrain_assessor",
                        output="screen",
                        parameters=parameters,
                        respawn=True,
                        respawn_delay=2.0,
                    )
                ],
            )
        )
    if _bool_arg(context, "nav"):
        actions.append(
            TimerAction(
                period=3.0,
                actions=[
                    Node(
                        package="rover_navigation",
                        executable="shared_autonomy",
                        name="shared_autonomy",
                        output="screen",
                        parameters=parameters,
                        respawn=True,
                        respawn_delay=2.0,
                    )
                ],
            )
        )
    if _bool_arg(context, "laser"):
        actions.append(
            TimerAction(
                period=3.2,
                actions=[
                    Node(
                        package="rover_navigation",
                        executable="laser_target_detector",
                        name="laser_target_detector",
                        output="screen",
                        parameters=parameters,
                        respawn=True,
                        respawn_delay=2.0,
                    )
                ],
            )
        )
    return actions


def generate_launch_description():
    bringup_share = get_package_share_directory("rover_bringup")
    default_params = os.path.join(bringup_share, "config", "rover_params.yaml")
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "profile",
                default_value="production",
                description="One of: sim, bench, field, production.",
            ),
            DeclareLaunchArgument("nav", default_value="true"),
            DeclareLaunchArgument("winch", default_value="true"),
            DeclareLaunchArgument("terrain", default_value="true"),
            DeclareLaunchArgument("laser", default_value="false"),
            DeclareLaunchArgument("params_file", default_value=default_params),
            LogInfo(msg="AXIOM ROVER MULO - INSTALLABLE BRINGUP"),
            OpaqueFunction(function=_launch_nodes),
        ]
    )


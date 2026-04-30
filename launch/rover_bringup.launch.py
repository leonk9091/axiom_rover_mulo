"""
Launch file principale - Axiom Rover "Mulo"
Avvia tutti i nodi nell'ordine corretto:
  1. safety_watchdog  (primo: deve essere attivo prima di tutto)
  2. stability_margin
  2. vesc_driver
  3. winch_manager
  4. power_monitor
  5. terrain_assessor
  6. shared_autonomy

Uso:
  ros2 launch rover_bringup rover_bringup.launch.py
  ros2 launch rover_bringup rover_bringup.launch.py sim:=true
  ros2 launch rover_bringup rover_bringup.launch.py nav:=false
"""
import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    TimerAction,
    LogInfo,
    GroupAction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # ---------------------------------------------------------------------------
    # Argomenti launch
    # ---------------------------------------------------------------------------
    arg_sim = DeclareLaunchArgument(
        'sim', default_value='false',
        description='Modalità simulazione (no hardware reale)'
    )
    arg_nav = DeclareLaunchArgument(
        'nav', default_value='true',
        description='Avvia nodo person following'
    )
    arg_winch = DeclareLaunchArgument(
        'winch', default_value='true',
        description='Avvia nodo winch manager'
    )
    arg_terrain = DeclareLaunchArgument(
        'terrain', default_value='true',
        description='Avvia terrain assessor'
    )
    arg_params = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config', 'rover_params.yaml'
        ),
        description='Path al file YAML dei parametri'
    )

    sim   = LaunchConfiguration('sim')
    nav   = LaunchConfiguration('nav')
    winch = LaunchConfiguration('winch')
    terrain = LaunchConfiguration('terrain')
    params_file = LaunchConfiguration('params_file')

    # ---------------------------------------------------------------------------
    # Nodo 1: Safety Watchdog (avvio immediato, nessun delay)
    # ---------------------------------------------------------------------------
    safety_watchdog_node = Node(
        package='rover_safety',
        executable='safety_watchdog',
        name='safety_watchdog',
        output='screen',
        parameters=[params_file],
        remappings=[],
        # Priorità alta: respawn se crasha
        respawn=True,
        respawn_delay=1.0,
    )

    # ---------------------------------------------------------------------------
    # Nodo 2: Stability Margin (delay 0.5s)
    # ---------------------------------------------------------------------------
    stability_margin_node = TimerAction(
        period=0.5,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio Stability Margin..."),
            Node(
                package='rover_safety',
                executable='stability_margin',
                name='stability_margin',
                output='screen',
                parameters=[params_file],
                respawn=True,
                respawn_delay=1.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Nodo 3: VESC Driver (delay 1s: attende safety watchdog)
    # ---------------------------------------------------------------------------
    vesc_driver_node = TimerAction(
        period=1.0,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio VESC Driver..."),
            Node(
                package='rover_control',
                executable='vesc_driver',
                name='vesc_driver',
                output='screen',
                parameters=[params_file],
                respawn=True,
                respawn_delay=2.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Nodo 4: Winch Manager (delay 2s)
    # ---------------------------------------------------------------------------
    winch_manager_node = TimerAction(
        period=2.0,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio Winch Manager..."),
            Node(
                package='rover_winch',
                executable='winch_manager',
                name='winch_manager',
                output='screen',
                parameters=[params_file],
                condition=IfCondition(winch),
                respawn=True,
                respawn_delay=2.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Nodo 5: Power Monitor (delay 2s)
    # ---------------------------------------------------------------------------
    power_monitor_node = TimerAction(
        period=2.0,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio Power Monitor (EKF + ECMS)..."),
            Node(
                package='rover_power',
                executable='power_monitor',
                name='power_monitor',
                output='screen',
                parameters=[params_file],
                respawn=True,
                respawn_delay=2.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Nodo 6: Terrain Assessor (delay 2.5s, opzionale)
    # ---------------------------------------------------------------------------
    terrain_assessor_node = TimerAction(
        period=2.5,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio Terrain Assessor..."),
            Node(
                package='rover_navigation',
                executable='terrain_assessor',
                name='terrain_assessor',
                output='screen',
                parameters=[params_file],
                condition=IfCondition(terrain),
                respawn=True,
                respawn_delay=2.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Nodo 7: Shared Autonomy (delay 3s, opzionale)
    # ---------------------------------------------------------------------------
    shared_autonomy_node = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg="[LAUNCH] Avvio Shared Autonomy (terrain-aware follow leader)..."),
            Node(
                package='rover_navigation',
                executable='shared_autonomy',
                name='shared_autonomy',
                output='screen',
                parameters=[params_file],
                condition=IfCondition(nav),
                respawn=True,
                respawn_delay=2.0,
            )
        ]
    )

    # ---------------------------------------------------------------------------
    # Robot State Publisher (URDF)
    # ---------------------------------------------------------------------------
    urdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'src', 'rover_description', 'urdf', 'axiom_rover.urdf'
    )
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': open(urdf_path).read()}]
        if os.path.exists(urdf_path) else [],
    )

    # ---------------------------------------------------------------------------
    # Log avvio
    # ---------------------------------------------------------------------------
    log_start = LogInfo(msg=(
        "\n"
        "╔══════════════════════════════════════════╗\n"
        "║   AXIOM ROVER 'MULO' - BRINGUP START    ║\n"
        "╚══════════════════════════════════════════╝"
    ))

    return LaunchDescription([
        # Argomenti
        arg_sim, arg_nav, arg_winch, arg_terrain, arg_params,
        # Log
        log_start,
        # Nodi (in ordine di priorità)
        safety_watchdog_node,
        stability_margin_node,
        robot_state_publisher,
        vesc_driver_node,
        winch_manager_node,
        power_monitor_node,
        terrain_assessor_node,
        shared_autonomy_node,
    ])

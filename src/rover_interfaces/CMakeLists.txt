cmake_minimum_required(VERSION 3.8)
project(rover_interfaces)

find_package(ament_cmake REQUIRED)
find_package(action_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/WinchStatus.msg"
  "msg/MotorTelemetry.msg"
  "msg/TerrainInfo.msg"
  "msg/SafetyStatus.msg"
  "msg/PowerSplit.msg"
  "msg/RoverState.msg"
  "msg/TerrainCost.msg"
  "msg/StabilityMargin.msg"
  "msg/EnergyBudget.msg"
  "msg/RangeExtenderStatus.msg"
  "msg/FaultReport.msg"
  "msg/HardwareState.msg"
  "msg/McuStatus.msg"
  "msg/SafetyCommand.msg"
  "msg/WinchCommand.msg"
  "msg/WinchState.msg"
  "msg/SafetyState.msg"
  "msg/LinkState.msg"
  "action/FollowLeader.action"
  "action/TraversePath.action"
  "action/AssistWinchTraverse.action"
  "action/SafeStop.action"
  "srv/ResetEstop.srv"
  "srv/CalibrateLoadCell.srv"
  DEPENDENCIES std_msgs geometry_msgs action_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()

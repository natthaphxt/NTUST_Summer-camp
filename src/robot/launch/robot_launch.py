"""
A launch file for running the motion planning python api tutorial with Ignition Gazebo 6 support
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    # 1. ดึงข้อมูลคอนฟิกทั้งหมดของ MoveIt
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="rrr_robot_arm_with_gripper",
            package_name="motion_robot_moveit_config",
        )
        .robot_description(file_path="config/rrr_robot_arm_with_gripper.urdf.xacro")
        .trajectory_execution(file_path="config/ros2_controllers.yaml")
        .to_moveit_configs()
    )

    # 2. ตั้งค่าการรันสคริปต์ Python API
    script_file = DeclareLaunchArgument(
        "script_file",
        default_value="moveit_py_example_node",
        description="Python API script file name",
    )

    parameters = moveit_config.to_dict()
    parameters["use_sim_time"] = True

    # 3. สั่งรัน Ignition Gazebo
    ignition_gazebo = ExecuteProcess(
        cmd=["ign", "gazebo", "-r", "empty.sdf"], output="screen"
    )

    # 4. Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description, {"use_sim_time": True}],
    )

    # 5. Spawn หุ่นยนต์หลังรอ 3 วินาที
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name",
                    "rrr_robot_arm_with_gripper",
                    "-topic",
                    "/robot_description",
                    "-world",
                    "empty",
                ],
                output="screen",
            )
        ],
    )

    # 6. ✅ Controller Spawners — รอ 5 วิให้ Gazebo + spawn เสร็จก่อน
    load_controllers = TimerAction(
        period=5.0,
        actions=[
            # joint_state_broadcaster ต้องโหลดก่อนเสมอ
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "joint_state_broadcaster",
                    "--controller-manager",
                    "/controller_manager",
                ],
                output="screen",
            ),
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "arm_controller",
                    "--controller-manager",
                    "/controller_manager",
                ],
                output="screen",
            ),
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "gripper_controller",
                    "--controller-manager",
                    "/controller_manager",
                ],
                output="screen",
            ),
        ],
    )

    # 7. Move Group Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.trajectory_execution,
            moveit_config.planning_scene_monitor,
            moveit_config.joint_limits,
            {"use_sim_time": True},
        ],
    )

    # 8. RViz2
    rviz_config_file = os.path.join(
        get_package_share_directory("motion_robot_moveit_config"),
        "config",
        "moveit.rviz",
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            {"use_sim_time": True},
        ],
    )

    # 9. MoveIt Python API node (เปิด comment เมื่อพร้อม)
    moveit_py_node = Node(
        name="moveit_py",
        package="motion_robot_moveit_config",
        executable=LaunchConfiguration("script_file"),
        output="both",
        parameters=[parameters],
    )

    return LaunchDescription(
        [
            script_file,
            ignition_gazebo,
            robot_state_publisher,
            spawn_robot,
            load_controllers,  # ✅ โหลด controller หลัง spawn
            move_group_node,
            rviz_node,
            # moveit_py_node,
        ]
    )

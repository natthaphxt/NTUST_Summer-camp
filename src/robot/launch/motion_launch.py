#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # 1. Get the package share directory for your 'robot' package
    pkg = get_package_share_directory("robot")

    # 2. Configure RViz2 node with the correct config path
    rviz_path = os.path.join(pkg, "config", "description_test.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_path],
        output="screen",
    )

    # 3. Read the text content of your URDF file safely using standard Python
    urdf_path = os.path.join(pkg, "urdf", "description_test.urdf")
    with open(urdf_path, "r") as infp:
        robot_desc = infp.read()

    # 4. Configure the robot_state_publisher node
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_desc}],
    )

    # 5. Configure your custom motion trajectory node (replaces the GUI)
    motion = Node(
        package="robot",  # Your ROS 2 package name
        executable="robot_motion.py",  # The executable name registered in setup.py
        name="motion_node",
        output="screen",
    )

    # Create the launch description and add actions
    launch_description = LaunchDescription()
    launch_description.add_action(rviz)
    launch_description.add_action(robot_state_publisher)
    launch_description.add_action(motion)

    return launch_description

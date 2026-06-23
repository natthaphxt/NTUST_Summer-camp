#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math


class MotionNode(Node):
    def __init__(self):
        super().__init__("motion_node")

        self.publisher_ = self.create_publisher(JointState, "joint_states", 10)

        self.timer_period = 0.05
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.waypoints = [
            [0.0, 0.0, 0.0, 0.0, 0.0],  
            [1.57, 0.5, -0.5, -0.02, 0.02], 
            [3.14, 1.0, -1.0, -0.04, 0.04], 
            [0.0, -0.5, 0.5, 0.0, 0.0], 
            [-1.57, 0.0, 0.0, -0.02, 0.02],
        ]
        self.current_waypoint_idx = 0
        self.next_waypoint_idx = 1
        self.interpolation_time = 2.0 
        self.elapsed_time = 0.0

    def timer_callback(self):
        self.elapsed_time += self.timer_period
        t = self.elapsed_time / self.interpolation_time

        if t >= 1.0:
            t = 1.0
            self.elapsed_time = 0.0
            self.current_waypoint_idx = self.next_waypoint_idx
            self.next_waypoint_idx = (self.next_waypoint_idx + 1) % len(self.waypoints)
        start_wp = self.waypoints[self.current_waypoint_idx]
        end_wp = self.waypoints[self.next_waypoint_idx]

        current_positions = []
        for start_pos, end_pos in zip(start_wp, end_wp):
            pos = start_pos + t * (end_pos - start_pos)
            current_positions.append(pos)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = [
            "base_to_rod1",
            "rod1_to_rod2",
            "rod2_to_rod3",
            "rod3_to_left_finger",
            "rod3_to_right_finger",
        ]
        msg.position = current_positions

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

#!/usr/bin/python3

from motion_robot.dummy_module import dummy_function, dummy_var
import rclpy
from rclpy.node import Node


class motion(Node):
    def __init__(self):
        super().__init__("motion_node")
        


def main(args=None):
    rclpy.init(args=args)
    node = motion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

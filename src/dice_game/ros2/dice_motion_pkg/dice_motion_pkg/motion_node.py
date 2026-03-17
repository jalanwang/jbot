import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool, Int32


class DiceMotionNode(Node):
    def __init__(self):
        super().__init__('dice_motion')

        self.declare_parameter('result_topic', '/eye/result')
        self.declare_parameter('ready_topic', '/dice/ready')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('angular_speed_deg', 30.0)
        self.declare_parameter('pause_seconds', 0.15)
        self.declare_parameter('timer_period', 0.05)

        result_topic = self.get_parameter('result_topic').value
        ready_topic = self.get_parameter('ready_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        angular_speed_deg = float(self.get_parameter('angular_speed_deg').value)
        self.pause_seconds = float(self.get_parameter('pause_seconds').value)
        timer_period = float(self.get_parameter('timer_period').value)
        self.angular_speed = math.radians(angular_speed_deg)

        self.cmd_vel_publisher = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.ready_publisher = self.create_publisher(Bool, ready_topic, 10)
        self.create_subscription(Int32, result_topic, self.result_callback, 10)

        self.motion_active = False
        self.motion_sequence = []
        self.motion_step_index = 0
        self.motion_step_started = None
        self.timer = self.create_timer(timer_period, self.motion_timer_callback)

        self.publish_ready(True)
        self.get_logger().info(
            f'Dice motion started. result_topic={result_topic}, cmd_vel_topic={cmd_vel_topic}'
        )

    def publish_ready(self, is_ready):
        msg = Bool()
        msg.data = is_ready
        self.ready_publisher.publish(msg)

    def publish_twist(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.cmd_vel_publisher.publish(msg)

    def build_motion_sequence(self, dice_value):
        turn_15_duration = math.radians(15.0) / self.angular_speed
        turn_30_duration = math.radians(30.0) / self.angular_speed
        sequence = []

        for _ in range(dice_value):
            sequence.extend([
                {'duration': turn_15_duration, 'angular_z': self.angular_speed},
                {'duration': self.pause_seconds, 'angular_z': 0.0},
                {'duration': turn_30_duration, 'angular_z': -self.angular_speed},
                {'duration': self.pause_seconds, 'angular_z': 0.0},
                {'duration': turn_15_duration, 'angular_z': self.angular_speed},
                {'duration': self.pause_seconds, 'angular_z': 0.0},
            ])

        return sequence

    def start_motion(self, dice_value):
        self.motion_active = True
        self.motion_sequence = self.build_motion_sequence(dice_value)
        self.motion_step_index = 0
        self.motion_step_started = None
        self.publish_ready(False)
        self.get_logger().info(f'Starting motion for dice result {dice_value}')

    def finish_motion(self):
        self.publish_twist(0.0, 0.0)
        self.publish_ready(True)
        self.motion_active = False
        self.motion_sequence = []
        self.motion_step_index = 0
        self.motion_step_started = None
        self.get_logger().info('Motion finished. Detector can resume.')

    def result_callback(self, msg):
        dice_value = int(msg.data)
        self.get_logger().info(f'Received dice result: {dice_value} (motion_active={self.motion_active})')

        if self.motion_active:
            self.get_logger().info('Ignoring dice result while motion is active.')
            return

        if dice_value < 1 or dice_value > 6:
            self.get_logger().warning(f'Ignoring out-of-range dice result: {dice_value}')
            return

        self.start_motion(dice_value)

    def motion_timer_callback(self):
        if not self.motion_active:
            return

        if self.motion_step_index >= len(self.motion_sequence):
            self.finish_motion()
            return

        step = self.motion_sequence[self.motion_step_index]
        now = time.monotonic()

        if self.motion_step_started is None:
            self.motion_step_started = now

        self.publish_twist(0.0, step['angular_z'])

        if now - self.motion_step_started >= step['duration']:
            self.motion_step_index += 1
            self.motion_step_started = None
            self.get_logger().info(f'Motion step {self.motion_step_index} completed')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DiceMotionNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.publish_twist(0.0, 0.0)
            node.publish_ready(True)
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

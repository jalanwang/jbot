# ~/robot/robot_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/move_turtle_with_detecting_obstacle.py
# 라이다 센서 데이터를 구독
# 터틀을 움직이게 한다.
# 현재 180를 바라보고 있다.
# 0.3m 이내에 장애물이 있으면 멈춘다.
# 수정중

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

# import termios
# import tty
# import os
# import select
# import sys

from my_turtlebot_pkg.my_package.my_utilz import KeyParser
# KeyParser 클래스는 키보드 입력을 비동기적으로 처리하기 위한 유틸리티 클래스.

class MoveTurtle(Node):
  def __init__(self):
    super().__init__('move_turtle_with_detecting_obstacle')

    self.qos_profile = QoSProfile(depth = 10)
    self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', self.qos_profile)
    # cmd_vel_publisher는 Twist 메시지를 /cmd_vel 토픽에 발행하는 퍼블리셔 인터페이스

    self.has_scan_received = False # 라이다 데이터를 받았는지 여부를 추적하는 플래그
    self.qos_profile = QoSProfile(depth = 10)
    self.scan_sub = self.create_subscription(
      LaserScan,
      '/scan',
      self.scan_callback,
      qos_profile=qos_profile_sensor_data)

    self.velocity = 0.0
    self.angular = 0.0
    #self.settings = termios.tcgetattr(sys.stdin)
    self.key_parser = KeyParser()
    self.scan_ranges = []

  def scan_callback(self, msg):
    self.scan_ranges = msg.ranges
    self.has_scan_received = True
    scan_range = len(self.scan_ranges) -1 # 라이다 데이터의 개수
    left_range = int(scan_range / 4)
    right_range = int(scan_range * 3 / 4)
    left_min = min(self.scan_ranges[0:left_range])
    # 라이다 우회전, 전방 정면에서 오른쪽 90도 까지
    right_min = min(self.scan_ranges[right_range:scan_range])
    # 라이다 우회전, 전방 정면에서 왼쪽 90도 까지
    self.get_logger().info(f'left_min:{left_min},right_min: {right_min}', throttle_duration_sec=2)
    self.get_logger().info(f'viewAngle: {len(self.scan_ranges)}', throttle_duration_sec=2)

  def turtle_key_move(self):
    count = 0
    msg = Twist()
    print("input wasdx")
    while True:
      #input_key = self.get_key(self.settings)
      input_key = self.key_parser.get_key()
      if input_key in ['w','W']:
        count += 1
        self.velocity += 0.1
        self.get_logger().info(f'Published message: {msg.linear}, {msg.angular}')
      elif input_key in ['s','S']:
        self.velocity = 0.0
        self.angular = 0.0
        count += 1
        self.get_logger().info(f'Published message: {msg.linear}, {msg.angular}')
      elif input_key in ['x','X']:
        self.velocity += -0.1
        count += 1
        self.get_logger().info(f'Published message: {msg.linear}, {msg.angular}')
      elif input_key in ['a','A']:
        self.angular += 0.1
        count += 1
        self.get_logger().info(f'Published message: {msg.linear}, {msg.angular}')
      elif input_key in ['d','D']:
        self.angular -= 0.1
        count += 1
        self.get_logger().info(f'Published message: {msg.linear}, {msg.angular}')
      elif input_key == '\x03':
        break

      msg.linear.x = self.velocity
      msg.linear.y = 0.0
      msg.linear.z = 0.0

      msg.angular.x = 0.0
      msg.angular.y = 0.0
      msg.angular.z = self.angular
      self.cmd_vel_publisher.publish(msg)
      if count == 20:
        print("input wasd")

def main(args=None):
  rclpy.init(args=args)
  node = MoveTurtle()
  try:
    node.turtle_key_move()
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard interrupt!!!!')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()

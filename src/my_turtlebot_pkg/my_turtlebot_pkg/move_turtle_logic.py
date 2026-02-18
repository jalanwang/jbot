# ~/robot/robot_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/move_turtle_logic.py
# 라이다 센서 데이터를 구독
# 터틀을 움직이게 한다.
# 현재 정면 좌우 45도씩 바라보고 있다.
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

class MoveTurtleLogic(Node):
  def __init__(self):
    super().__init__('move_turtle_logic')

    self.qos_profile = QoSProfile(depth = 10)
    self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', self.qos_profile)
    # cmd_vel_publisher는 Twist 메시지를 /cmd_vel 토픽에 발행하는 퍼블리셔 인터페이스

    self.has_scan_received = False # 라이다 데이터를 받았는지 여부를 추적하는 플래그
    self.qos_profile = QoSProfile(depth = 10)
    self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, qos_profile=qos_profile_sensor_data)
    # scan_sub는 LaserScan 메시지를 /scan 토픽에서 구독하는 서브스크라이버 인터페이스.
    # qos_profile_sensor_data는 센서 데이터에 적합한 QoS 설정을 사용.

    self.velocity = 0.0
    self.angular = 0.0
    self.key_parser = KeyParser() # KeyParser 클래스의 인스턴스를 생성하여 키보드 입력을 처리하는 객체를 초기화
    self.scan_ranges = [] # 라이다 데이터의 범위를 저장하는 리스트
    self.front_min = 0.0 # 라이다 데이터에서 전방의 최소 거리값을 저장하는 변수

  def scan_callback(self, msg):
    #라이다 CW 가정
    self.scan_ranges = msg.ranges
    self.has_scan_received = True
    scan_range = len(self.scan_ranges) -1 # 라이다 데이터의 개수
    right_range = int(scan_range / 8) # 45도
    left_range = int(scan_range * 7 / 8) # one round -45도

    front_ranges = self.scan_ranges[0:right_range] + self.scan_ranges[left_range:]

    self.front_min = min(front_ranges) # 전방의 최소 거리값을 계산하여 front_min 변수에 저장

  def is_obstacle_ahead(self):
    if not self.has_scan_received:
      return False

    return self.front_min < 0.3
    # 장애물이 0.3m 이내에 있으면 True 반환, 그렇지 않으면 False 반환

  def turtle_key_move(self):
    msg = Twist()
    print("input wasdx")
    while True:
      rclpy.spin_once(self, timeout_sec=0)
      # ROS2 이벤트 루프(머 들어온것 있어?)를 한 번 실행하여 콜백 함수가 호출되도록 함
      # 돌아오면 바로 아래로 돌아가도록 타임아웃 0 설정

      input_key = self.key_parser.get_key()
      if input_key in ['w','W']:
        self.velocity += 0.1
      elif input_key in ['s','S']:
        self.velocity = 0.0
        self.angular = 0.0
      elif input_key in ['x','X']:
        self.velocity += -0.1
      elif input_key in ['a','A']:
        self.angular += 0.1
      elif input_key in ['d','D']:
        self.angular -= 0.1
      elif input_key == '\x03':
        break

      msg.linear.x = self.velocity
      msg.linear.y = 0.0
      msg.linear.z = 0.0

      msg.angular.x = 0.0
      msg.angular.y = 0.0
      msg.angular.z = self.angular

      if(self.is_obstacle_ahead() and self.velocity > 0):
        self.get_logger().info(f'Obstacle 발견!: {self.front_min}', throttle_duration_sec=1)
        self.velocity = 0.0 # 필요 없는 것 같은데 일단 넣어봄. 장애물이 앞에 있으면 속도를 0으로 설정하여 멈추게 함
        self.angular = 0.0 # 필요 없는 것 같은데 일단 넣어봄. 장애물이 앞에 있으면 회전 속도도 0으로 설정하여 멈추게 함
        msg.linear.x = 0.0
        msg.angular.z = 0.0
      elif(not self.is_obstacle_ahead()):
        self.get_logger().info(f'No Obstacle: {self.front_min}', throttle_duration_sec=1)
      self.cmd_vel_publisher.publish(msg) # cmd_vel 토픽에 Twist 메시지를 발행하여 터틀봇의 속도와 회전 속도를 제어

def main(args=None):
  rclpy.init(args=args)
  node = MoveTurtleLogic()
  try:
    node.turtle_key_move()
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard interrupt!!!!')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
	  main()


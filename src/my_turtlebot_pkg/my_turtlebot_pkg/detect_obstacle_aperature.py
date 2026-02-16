# ~/turtlebot3_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/detect_obstacle_aperature.py
# 장애물 감지 노드. 라이다가 바라보는 영역을 4등분하여 최솟값을 구한다.
# 라이다 센서 데이터를 사용하여 장애물을 감지합니다.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class DetectTurtleAperature(Node):
  def __init__(self):
    super().__init__('detect_turtle_aperature')
    self.has_scan_received = False # 라이다 데이터를 받았는지 여부를 추적하는 플래그
    self.qos_profile = QoSProfile(depth = 10)
    self.scan_sub = self.create_subscription(
      LaserScan,
      '/scan',
      self.scan_callback,
      qos_profile=qos_profile_sensor_data)
    self.velocity = 0.0
    self.angular = 0.0
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


def main(args=None):
  rclpy.init(args=args)
  node = DetectTurtleAperature()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard interrupt!!!!')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
	  main()


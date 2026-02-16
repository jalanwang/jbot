# ~/turtlebot3_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/detect_obstacle.py
# 장애물 감지 노드입니다.
# 라이다 센서 데이터를 사용하여 장애물을 감지합니다.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class DetectTurtle(Node):
  def __init__(self):
    super().__init__('detect_turtle')
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
    self.get_logger().info(f'scanData: {self.scan_ranges[0]}', throttle_duration_sec=2)
    # 로그는 2초마다 남긴다. 너무 자주 남기면 로그 보기가 힘들다.

def main(args=None):
  rclpy.init(args=args)
  node = DetectTurtle()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard interrupt!!!!')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
	  main()

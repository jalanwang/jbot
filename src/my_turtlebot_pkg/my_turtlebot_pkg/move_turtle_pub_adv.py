# ~/robot_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/move_turtle_pub.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class MoveTurtle(Node):
  def __init__(self):
    super().__init__('move_turtle')
    self.qos_profile = QoSProfile(depth = 10)
    self.move_turtle = self.create_publisher(Twist, '/cmd_vel', self.qos_profile)
    self.velocity = 0.0
    self.angular = 0.0
    # self.timer = self.create_timer(1, self.turtle_move)
    # self.turtle_key_move()

  def turtle_move(self):
    msg = Twist()
    msg.linear.x = self.velocity
    msg.linear.y = 0.0
    msg.linear.z = 0.0

    msg.angular.x = 0.0
    msg.angular.y = 0.0
    msg.angular.z = 1.0
    self.move_turtle.publish(msg)
    self.get_logger().info(f'Published mesage: {msg.linear}, {msg.angular}')
    self.velocity += 0.08
    if self.velocity > 2:
      self.velocity = 0.0

  def turtle_key_move(self):
    while True:
      # input keyboard to control trutle ('w','a','s','d','x')
      key = input("Enter command: ")
      if key == 'w' or key == 'W':
        self.velocity += 0.01
      elif key == 'a' or key == 'A':
        self.angular += 0.1
      elif key == 's' or key == 'S':
        self.velocity = 0.0
        self.angular = 0.0
      elif key == 'd' or key == 'D':
        self.angular -= 0.1
      elif key == 'x' or key == 'X':
        self.velocity -= 0.01

      msg = Twist()
      msg.linear.x = self.velocity
      msg.linear.y = 0.0
      msg.linear.z = 0.0
      msg.angular.x = 0.0
      msg.angular.y = 0.0
      msg.angular.z = self.angular
      self.move_turtle.publish(msg)
      self.get_logger().info(f'Pub: v={msg.linear.x:.2f}, w={msg.angular.z:.2f}')


def main(args=None):
  rclpy.init(args=args)
  node = MoveTurtle()
  try:
    # rclpy.spin(node) # Use spin if using timer or callbacks
    node.turtle_key_move() # Call function directly for blocking input
  except KeyboardInterrupt:
    node.get_logger().info('Keyboard interrupt!!!!')
  finally:
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()

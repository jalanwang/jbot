# ~/turtlebot3_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/lidar_subscriber.py
# 라이다 센서 데이터를 구독하는 노드입니다.
# LaserScan 메시지 타입을 사용하여 라이다 데이터를 처리한다.
# 현재 정면만 바라보고 있다.

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy # QoS 설정을 위해 추가
from sensor_msgs.msg import LaserScan # String 대신 LaserScan을 가져옴

class LidarSubscriber(Node):

    def __init__(self):
        super().__init__('lidar_subscriber')

        # 2. 라이다 데이터는 신뢰성(Reliability) 옵션이 중요할 수 있어 설정을 정교하게 함
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, # 가제보 환경에 따라 다를 수 있음
            depth=10
        )

        self.lidar_subscriber = self.create_subscription(
            LaserScan,      # 3. 타입을 String에서 LaserScan으로 변경
            'scan',         # 4. 토픽 이름을 'helloworld'에서 'scan'으로 변경
            self.subscribe_topic_message,
            qos_profile)

    def subscribe_topic_message(self, msg):
        # 5. LaserScan은 msg.data가 아니라 msg.ranges에 거리 데이터가 배열로 들어간다.
        # 정면(0도)의 거리 값을 출력.
        self.get_logger().info('정면 거리: {0} m'.format(msg.ranges[0]))

def main(args=None):
    rclpy.init(args=args)
    node = LidarSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

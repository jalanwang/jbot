import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

class ImageSubscriber(Node):
    def __init__(self, callback_func):
        super().__init__('image_subscriber')
        self.bridge = CvBridge()
        self.callback_func = callback_func # 중앙 서버로 데이터를 보낼 통로

        # 터틀봇 카메라 데이터 수신에 최적화된 QoS (기존 설정 유지)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.VOLATILE
        )

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            qos_profile)

        self.get_logger().info('이미지 구독 및 인코딩 처리 노드가 시작되었습니다.')

    def listener_callback(self, data):
        try:
            # 1. 원본 데이터 가져오기 (기존 로직 복구)
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='passthrough')

            # 2. 인코딩 타입에 따른 색상 변환 처리
            # 터틀봇 카메라가 쏘는 데이터 형식에 맞춰 BGR로 통일합니다.
            if data.encoding in ['yuv422', 'yuyv', 'yuv422_yuy2']:
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_YUV2BGR_YUYV)
            elif data.encoding == 'rgb8':
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            # 만약 이미 bgr8이라면 별도의 변환 없이 진행됩니다.

            # 3. 유효성 검사 후 중앙 서버 콜백 호출
            if cv_image is not None and cv_image.size > 0:
                self.callback_func(cv_image)

        except Exception as e:
            self.get_logger().error(f'이미지 인코딩/처리 에러: {e}')

def main(args=None):
    os.environ['QT_X11_NO_MITSHM'] = '1'
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()

    try:
        rclpy.spin(image_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        image_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

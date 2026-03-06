import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2

class IriunPublisher(Node):
    def __init__(self):
        super().__init__('iriun_publisher')
        # 이미지와 카메라 정보를 발행할 퍼블리셔 설정
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.info_pub = self.create_publisher(CameraInfo, '/camera/camera_info', 10)
        self.br = CvBridge()

        # Iriun이 잡힌 /dev/video2 장치 열기
        self.cap = cv2.VideoCapture(2)

        # 장치 지원 해상도인 1280x720으로 강제 설정
        self.width = 1280
        self.height = 720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # 동기화를 위한 기본 카메라 정보 설정
        self.camera_info = CameraInfo()
        self.camera_info.header.frame_id = "camera_link"
        self.camera_info.width = self.width
        self.camera_info.height = self.height

        # 30fps 속도로 타이머 실행
        self.timer = self.create_timer(1/30, self.timer_callback)
        self.get_logger().info('Iriun Publisher (1280x720) 시작됨')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # 두 토픽의 타임스탬프를 동일하게 맞춰서 경고 발생 방지
            now = self.get_clock().now().to_msg()

            # 이미지 메시지 발행
            img_msg = self.br.cv2_to_imgmsg(frame, encoding="bgr8")
            img_msg.header.stamp = now
            img_msg.header.frame_id = "camera_link"
            self.image_pub.publish(img_msg)

            # 카메라 정보 발행
            self.camera_info.header.stamp = now
            self.info_pub.publish(self.camera_info)

def main(args=None):
    rclpy.init(args=args)
    node = IriunPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.cap.release()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

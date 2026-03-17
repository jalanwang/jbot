import rclpy
import sys
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
import cv2
import os
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class TurtleYOLONode(Node):
    def __init__(self, model_path, target=None, callback_func=None):
        super().__init__('turtle_yolo_node')

        # 확인한 경로 사용
        self.model = None
        self.model_ready = False # 모델 상태 플래그
        self.bridge = CvBridge()
        self.callback_func = callback_func
        self.target = target
        self.td_signal = False
        self.start_signal = False
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT, # 손실 감수, 실시간성 우선
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # 터틀봇 카메라 토픽 구독
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # 토픽 이름
            self.image_callback,
            qos_profile)

        # self.subscription = self.create_subscription(
        #     CompressedImage,           # CompressedImage
        #     '/camera/image_raw/compressed',   # 토픽 이름
        #     self.image_callback,
        #     qos_profile)

        # 모델 생성 전 학습파일이 있는지 먼저 확인
        if os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                self.model_ready = True
                self.get_logger().info(f"모델 로드 완료: {model_path}")
            except ImportError:
                self.get_logger().error('ultralytics 패키지가 없어 YOLO를 비활성화합니다.')
            except Exception as e:
                self.get_logger().error(f"모델 로드 실패: {e}")
        else:
            # 파일이 없으면 경고 메시지만 출력 (노드는 죽이지 않음)
            self.get_logger().warn(f"모델 파일이 없습니다: {model_path}")

        self.get_logger().info('YOLO 인식 노드가 시작되었습니다!')

    def image_callback(self, msg):
        try:
            # ROS 영상을 OpenCV 형식으로 변환
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            # frame = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
            #print(frame.shape[1])
            annotated_frame = frame
            detected_classes = []
            if self.start_signal:
                if self.model_ready:
                    # YOLO 추론 진행
                    # results = self.model(frame, stream=True)
                    results = self.model(frame, stream=True, conf=0.5)
                    for r in results:
                        annotated_frame = r.plot()  # 인식 결과(주석이 붙은)가 그려진 프레임

                        # 인식된 객체들의 class name 추출
                        for box in r.boxes:
                            cls_id = int(box.cls[0])           # 클래스 번호
                            cls_name = self.model.names[cls_id] # 클래스 이름 (예: 'person', 'stop sign')
                            detected_classes.append(cls_name)
                else:
                    pass

                if self.target and self.model_ready:
                    if any(cls in detected_classes for cls in self.target):
                        self.td_signal = True
                    else:
                        self.td_signal = False
            else:
                pass

            # 만약 UI 갱신용 콜백이 연결되어 있다면 호출
            if self.callback_func and self.model_ready:
                self.callback_func(annotated_frame, self.td_signal)
            else:
                pass

        except Exception as e:
            self.get_logger().error(f'YOLO 처리 중 오류 발생: {e}')

    def set_start_mode(self):
        self.start_signal = True

    def set_pause_mode(self):
        self.start_signal = False
        self.td_signal = False

def main(args=None):
    rclpy.init(args=args)
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'yolov8n.pt')
    node = TurtleYOLONode(model_path=model_path)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

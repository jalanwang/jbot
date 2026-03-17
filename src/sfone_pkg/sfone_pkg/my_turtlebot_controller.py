import sys
import rclpy
import cv2
import pygame
import os
import io
import time
try:
    from gtts import gTTS
except ImportError:
    gTTS = None
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from turtlebot3_msgs.srv import Sound
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from rclpy.executors import MultiThreadedExecutor
from cv_bridge import CvBridge

# ros2 의 module 참조방식
from .turtlebot_controller_ui import Ui_Form
from .my_auto_drive import AutoDrive
from .my_image_sub import ImageSubscriber
from .my_turtle_yolo import TurtleYOLONode
from .my_window import CameraWindow

# GUI 의 쓰레드와 충돌을 피하기위해 qthread를 상속받아서 rclpy 쓰레드를 구성
class RclpyThread(QThread):
    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def run(self):
        try:
            self.executor.spin()
        finally:
            if rclpy.ok():
                rclpy.shutdown()

class MyTurtlebot3Controller(QWidget):
    def __init__(self, model_path):
        # ui에 관한 코드
        super(MyTurtlebot3Controller, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.camera_win = CameraWindow()

        # rclpy 쓰레드를 실행
        rclpy.init()
        qos_profile = QoSProfile(depth=10)
        self.velocity = 0.0
        self.rotation = 0.0

        # image 처리 멤버
        self.current_frame = None
        self.bridge = CvBridge()
        self.img_sub_node = ImageSubscriber(self.image_callback)
        self.sound_node = Node("Sound_client")
        self.Sound_client = self.sound_node.create_client(Sound, '/sound')
        self.detection_target = ["person"]
        self.yolo_model_path = model_path
        self.detected_frame = None
        self.last_detection_time = time.time()
        self.detection_term = 10.0
        self.target_detected_prev = False
        pygame.mixer.init()
        self.fp = None

        # button publisher Page 정의
        self.btn_pub_node = Node("Button_publisher")
        self.Button_publisher = self.btn_pub_node.create_publisher(Twist, '/cmd_vel', qos_profile)
        self.ui.go_BP.clicked.connect(self.go_BP_clicked)
        self.ui.btn_Go.clicked.connect(self.btn_pub_Go_clicked)
        self.ui.btn_Back.clicked.connect(self.btn_pub_Back_clicked)
        self.ui.btn_TRight.clicked.connect(self.btn_pub_TRight_clicked)
        self.ui.btn_TLeft.clicked.connect(self.btn_pub_TLeft_clicked)
        self.ui.btn_Stop.clicked.connect(self.btn_pub_Stop_clicked)
        self.ui.btn_MP.clicked.connect(self.btn_MP_clicked)

        # 충돌회피 Auto Drive Page 정의
        self.auto_pub_node = AutoDrive()
        self.auto_sub_node = Node("Driving_state_Subscriber")
        self.auto_sub = self.auto_sub_node.create_subscription(String, '/driving_state', self.state_callback, qos_profile)
        self.ui.go_AP.clicked.connect(self.go_AP_clicked)
        self.ui.btn_autoStart.clicked.connect(self.btn_autoStart_clicked)
        self.ui.btn_autoStop.clicked.connect(self.btn_autoStop_clicked)
        self.ui.btn_autoStop.setEnabled(False)
        self.ui.btn_MP_3.clicked.connect(self.btn_MP_clicked_inAP)
        self.last_state_msg = String()
        self.last_state_msg.data = "Stop"
        self.auto_pub_node.signals.Driving_status.connect(self.update_AP_button)

        # ObjectDetection Node 정의
        self.yolo_node = TurtleYOLONode(self.yolo_model_path, self.detection_target, callback_func=self.yolo_ui_callback)

        # MultiThread 설정
        self.executor = MultiThreadedExecutor(num_threads=12)

        # node 추가.
        self.executor.add_node(self.btn_pub_node)
        self.executor.add_node(self.auto_pub_node)
        self.executor.add_node(self.auto_sub_node)
        self.executor.add_node(self.img_sub_node)
        self.executor.add_node(self.yolo_node)
        self.executor.add_node(self.sound_node)

        # rclpy Thread 시작.
        self.rclpy_thread = RclpyThread(self.executor)
        self.rclpy_thread.start()

    def play_voice(self, text):
        if gTTS is None:
            print("gTTS is not installed. Voice playback is disabled.")
            return

        if pygame.mixer.music.get_busy():
            return

        try:
            self.fp = io.BytesIO()

            # gTTS 음성 생성 및 메모리에 쓰기
            tts = gTTS(text=text, lang='ko')
            tts.write_to_fp(self.fp)

            # 읽기 위치를 처음으로 이동
            self.fp.seek(0)

            # 재생 (self.fp를 인자로 전달하여 참조 유지)
            pygame.mixer.music.load(self.fp)
            pygame.mixer.music.play()

            # self.fp는 멤버 변수이므로 함수가 끝나도 메모리에서 해제되지 않습니다.

        except Exception as e:
            print(f"음성 재생 중 오류 발생: {e}")


    def open_camera_window(self):
        # 창이 이미 최소화되어 있으면 정상 크기로, 안 보이면 보이게
        if self.camera_win.isHidden():
            self.camera_win.show()
        else:
            self.camera_win.raise_() # 맨 앞으로 가져오기
            self.camera_win.activateWindow()

    def close_camera_window(self):
        # 창이 숨겨져 있지 않다면 (즉, 화면에 보이고 있다면)
        if not self.camera_win.isHidden():
            self.camera_win.hide()  # 창을 숨깁니다.
        else:
            pass

    def yolo_ui_callback(self, annotated_frame, td_signal):
        current_time = time.time()

        if td_signal:
            if current_time - self.last_detection_time > self.detection_term:
                self.play_voice("타겟 감지")
                request = Sound.Request()
                request.value = 3
                self.Sound_client.call_async(request)
                self.last_detection_time = current_time

        if annotated_frame is None:
            return

        self.detected_frame = annotated_frame

        try:
            # 1. Qt에서 크기를 맞추지 말고, 여기서 타겟 라벨 크기에 맞춰 미리 줄입니다.
            target_w = self.camera_win.ui.label_yolo_view.width()
            target_h = self.camera_win.ui.label_yolo_view.height()

            # 보간법을 INTER_LINEAR나 INTER_NEAREST로 설정 (가장 빠름)
            resized_frame = cv2.resize(annotated_frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

            # 2. BGR -> RGB 변환
            rgb_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            # 3. QImage 생성 (이미 크기가 맞으므로 scaled() 호출 불필요)
            h, w, ch = rgb_image.shape
            q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
            pixmap = QPixmap.fromImage(q_img)

            # # 1. BGR -> RGB 색상 변환
            # rgb_image = cv2.cvtColor(self.detected_frame, cv2.COLOR_BGR2RGB)

            # # 2. QImage로 변환
            # h, w, ch = rgb_image.shape
            # bytes_per_line = ch * w
            # # q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()

            # # 3. QPixmap으로 변환
            # pixmap = QPixmap.fromImage(q_img)

            # 4. YOLO 창이 열려 있을 때만 전송 (성능 최적화)
            if self.camera_win.isVisible():
                # # 창 크기에 맞춰 이미지 조절 (비율 유지)
                # # 만약 yolo_window.ui 내부의 QLabel 이름이 label_yolo_view 라면:
                # target_label = self.camera_win.ui.label_yolo_view

                # scaled_pixmap = pixmap.scaled(
                #     target_label.width(),
                #     target_label.height(),
                #     Qt.KeepAspectRatio,
                #     Qt.SmoothTransformation
                # )

                # # 최종적으로 이미지 세팅
                # self.camera_win.update_image(scaled_pixmap)
                # 4. 즉시 업데이트
                self.camera_win.update_image(pixmap)

        except Exception as e:
            print(f"이미지 변환 중 오류 발생: {e}")


    def image_callback(self, cv_image):
        """
        image_subscriber.py에서 인코딩 처리가 완료된 BGR 이미지가 일로 들어옵니다.
        """
        # 1. 중앙 서버 변수에 저장 (참조 복사라 오버헤드 거의 없음)
        self.current_frame = cv_image

    def send_to_predict_server(self):
        """
        중앙 서버에 저장된 최신 프레임을 외부 AI 서버로 전송하는 함수
        """
        if self.current_frame is not None:
            # 다른 서버로 보낼 때는 전송 중에 데이터가 변하지 않도록 복사본 권장
            frame_to_send = self.current_frame.copy()

            # 여기에 통신 로직 (HTTP POST / gRPC / ROS Service 등) 작성
            # 예: result = my_predictor.predict(frame_to_send)
            pass

    def update_AP_button(self, is_driving):
        self.ui.btn_autoStart.setEnabled(not is_driving)
        self.ui.btn_autoStop.setEnabled(is_driving)

    def go_BP_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.open_camera_window()
        # self.yolo_node.set_start_mode()

    def btn_MP_clicked(self):
        #임시
        self.velocity = 0.0
        self.rotation = 0.0
        self.pub_msg()
        self.close_camera_window()
        self.ui.stackedWidget.setCurrentIndex(0)

    def go_AP_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.open_camera_window()
        self.yolo_node.set_start_mode()

    def btn_MP_clicked_inAP(self):
        self.auto_pub_node.stop_drive()
        self.ui.list_Dlog.clear()
        self.last_state_msg.data = "Stop"
        self.close_camera_window()
        self.yolo_node.set_pause_mode()
        self.ui.stackedWidget.setCurrentIndex(0)

    def btn_autoStop_clicked(self):
        self.auto_pub_node.stop_drive()
        self.last_state_msg.data = "Stop"
        self.ui.list_Dlog.addItem(f"Turtlebot Status: {self.last_state_msg.data}.")

    def btn_autoStart_clicked(self):
        # self.ui.list_Dlog.clear()
        self.last_state_msg.data = "Stop"
        self.auto_pub_node.start_drive()

    def state_callback(self, msg):
        if msg.data != self.last_state_msg.data:
            self.last_state_msg.data = msg.data
            self.ui.list_Dlog.addItem(f"Turtlebot Status: {self.last_state_msg.data}.")

    def pub_msg(self):
        msg = Twist()
        msg.linear.x = self.velocity
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = self.rotation
        self.Button_publisher.publish(msg)
        self.btn_pub_node.get_logger().info(f'Published mesage: {msg.linear}, {msg.angular}')

    def btn_pub_Go_clicked(self):
        self.velocity = 0.05
        self.rotation = 0.0
        self.pub_msg()

    def btn_pub_Back_clicked(self):
        self.velocity = -0.05
        self.rotation = 0.0
        self.pub_msg()

    def btn_pub_TRight_clicked(self):
        self.velocity = 0.0
        self.rotation = -0.3
        self.pub_msg()

    def btn_pub_TLeft_clicked(self):
        self.velocity = 0.0
        self.rotation = 0.3
        self.pub_msg()

    def btn_pub_Stop_clicked(self):
        self.velocity = 0.0
        self.rotation = 0.0
        self.pub_msg()

    def closeEvent(self, event):
        # 종료 시 리소스 정리
        print("쓰레드 및 노드 종료")
        self.executor.shutdown()
        pygame.mixer.quit()
        self.rclpy_thread.quit()
        self.rclpy_thread.wait()
        self.btn_pub_node.destroy_node()
        self.auto_pub_node.destroy_node()
        self.auto_sub_node.destroy_node()
        self.img_sub_node.destroy_node()
        self.yolo_node.destroy_node()
        self.sound_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        super().closeEvent(event)

def main(args=None):
    app = QApplication(sys.argv)

    # 1. 인자가 들어왔는지 확인 (sys.argv[0]은 파일명임)
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        # 인자가 없을 경우 사용할 기본값
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_model_path = os.path.join(current_dir, 'yolov8n.pt')
        model_path = default_model_path
        print(f"Warning: No model path provided. Using default: {model_path}")

    window = MyTurtlebot3Controller(model_path)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



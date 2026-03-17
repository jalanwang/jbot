import os
import time

import cv2
import numpy as np
import rclpy
import tensorflow as tf
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from ultralytics import YOLO

from project_paths import resolve_model_file


def get_camera_info(camera_index):
    """카메라의 상세 정보 조회 - /sys 에서 직접 읽기"""
    try:
        with open(f'/sys/class/video4linux/video{camera_index}/name', 'r') as f:
            return f.read().strip()
    except Exception:
        return None


def detect_cameras_with_info():
    """사용 가능한 카메라 목록을 감지하고 상세 정보 포함"""
    available_cameras = {}
    for i in range(10):  # 최대 10개 카메라 검사
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resolution = f'{width}x{height}'

            # /sys에서 카메라 이름 읽기
            name = get_camera_info(i)
            if name is None:
                name = 'Unknown'

            available_cameras[i] = {'name': name, 'resolution': resolution}

            cap.release()
    return available_cameras


def find_logitech_camera(available_cameras):
    """로지텍 카메라를 찾아서 인덱스 반환"""
    for idx, info in available_cameras.items():
        name = info['name'].lower()
        # 로지텍 C920 또는 기타 로지텍 카메라 찾기
        if 'c920' in name or 'pro webcam' in name or 'logitech' in name:
            return idx
    return None


class EyeNumberUSBCameraNode(Node):
    def __init__(self):
        super().__init__('eye_number_usb_camera')

        self.declare_parameter('result_topic', '/eye/result')
        self.declare_parameter('confirmation_seconds', 0.5)
        self.declare_parameter('show_window', True)

        camera_index = '/dev/video3'  # 카메라 장치 경로 직접 지정 (v4l2-ctl --list-devices 로 확인)
        result_topic = self.get_parameter('result_topic').value
        self.confirmation_seconds = float(self.get_parameter('confirmation_seconds').value)
        self.show_window = bool(self.get_parameter('show_window').value)

        try:
            self.yolo_model = YOLO(str(resolve_model_file('yolov8n.pt')))
            self.dice_classifier = tf.keras.models.load_model(str(resolve_model_file('green_dice_model.keras')))
            self.get_logger().info(f'Models loaded successfully')
        except Exception as error:
            self.get_logger().error(f'Failed to load models: {error}')
            raise

        self.bridge = CvBridge()
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.dice_labels = ['1', '2', '3', '4', '5', '6']

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.get_logger().error(f'Failed to open camera at index {camera_index}')
            raise RuntimeError(f'Cannot open camera {camera_index}')

        # 카메라 자동 초점 활성화
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.get_logger().info(f'Camera autofocus enabled')

        self.result_publisher = self.create_publisher(Int32, result_topic, 10)
        self.pending_result = None
        self.pending_result_since = None
        self.last_detected = None

        timer_period = 0.033  # ~30 FPS
        self.timer = self.create_timer(timer_period, self.camera_timer_callback)

        self.get_logger().info(f'USB camera node started. camera_index={camera_index}, result_topic={result_topic}')

    def get_square_crop(self, frame, x1, y1, x2, y2, target_size=(100, 100)):
        """비율 왜곡 없이 원본에서 정사각형 영역을 추출하여 전처리"""
        h_orig, w_orig = frame.shape[:2]
        bw, bh = x2 - x1, y2 - y1
        cx, cy = x1 + bw // 2, y1 + bh // 2
        side = max(bw, bh)

        nx1 = max(0, cx - side // 2)
        ny1 = max(0, cy - side // 2)
        nx2 = nx1 + side
        ny2 = ny1 + side

        if nx2 > w_orig:
            nx2 = w_orig
            nx1 = max(0, nx2 - side)
        if ny2 > h_orig:
            ny2 = h_orig
            ny1 = max(0, ny2 - side)

        crop = frame[ny1:ny2, nx1:nx2]
        if crop.size == 0:
            return None

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
        enhanced = self.clahe.apply(resized)
        input_arr = enhanced.astype('float32') / 255.0
        return np.expand_dims(input_arr, axis=(0, -1))

    def update_pending_result(self, detected_result):
        """상태 변화 추적: 0(없음) 또는 1-6(감지된 값)"""
        current_state = detected_result if detected_result is not None else 0

        if self.last_detected != current_state:
            self.pending_result = current_state
            self.pending_result_since = time.monotonic()
            self.last_detected = current_state
            state_desc = f'Eye appeared: {current_state}' if current_state > 0 else 'Eye disappeared'
            self.get_logger().info(f'{state_desc} (starting confirmation)')
            return

        now = time.monotonic()
        if self.pending_result_since is None:
            self.pending_result_since = now

        if (now - self.pending_result_since) >= self.confirmation_seconds:
            msg = Int32()
            msg.data = current_state
            self.result_publisher.publish(msg)
            action = f'Published eye result: {current_state}' if current_state > 0 else 'Published eye disappearance: 0'
            self.get_logger().info(action)
            self.pending_result = None
            self.pending_result_since = None

    def camera_timer_callback(self):
        """카메라에서 프레임을 읽고 처리"""
        ret, frame = self.cap.read()
        if not ret:
            return

        try:
            results = self.yolo_model(frame, verbose=False)[0]
        except Exception as error:
            self.get_logger().error(f'Failed to process frame: {error}')
            return

        best_result = None
        best_confidence = -1.0

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([25, 10, 5])
        upper_green = np.array([105, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            bw, bh = x2 - x1, y2 - y1
            if bw <= 0 or bh <= 0:
                continue

            aspect_ratio = bw / bh
            roi_mask = green_mask[y1:y2, x1:x2]
            green_ratio = cv2.countNonZero(roi_mask) / float(bw * bh)

            if not (0.75 <= aspect_ratio <= 1.25):
                continue
            if bw >= 300 or bh >= 300:
                continue
            if green_ratio < 0.5:
                continue

            input_data = self.get_square_crop(frame, x1, y1, x2, y2)
            if input_data is None:
                continue

            preds = self.dice_classifier.predict(input_data, verbose=0)
            pred_class = int(np.argmax(preds))
            confidence = float(preds[0][pred_class])
            eye_val = int(self.dice_labels[pred_class])

            if confidence > best_confidence:
                best_confidence = confidence
                best_result = eye_val

            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            text = f'Eye: {eye_val} ({confidence * 100:.1f}%)'
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        self.update_pending_result(best_result)

        if self.show_window:
            if self.pending_result is not None and self.pending_result_since is not None:
                elapsed = time.monotonic() - self.pending_result_since
                confirm_text = (
                    f'Pending: {self.pending_result} '
                    f'({elapsed:.1f}/{self.confirmation_seconds:.1f}s)'
                )
                cv2.putText(frame, confirm_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow('USB Camera Eye Number Analysis', frame)
            cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = EyeNumberUSBCameraNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception:
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

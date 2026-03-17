import os
import sys
import time

import cv2
import numpy as np
import rclpy
import tensorflow as tf
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Int32
from ultralytics import YOLO

from .asset_paths import resolve_model_paths


class DiceDetectorNode(Node):
    def __init__(self):
        super().__init__('dice_detector')

        self.declare_parameter('camera_topic', '/camera/image_raw')
        self.declare_parameter('result_topic', '/dice/result')
        self.declare_parameter('ready_topic', '/dice/ready')
        self.declare_parameter('confirmation_seconds', 1.0)
        self.declare_parameter('green_ratio_threshold', 0.4)
        self.declare_parameter('square_ratio_min', 0.8)
        self.declare_parameter('square_ratio_max', 1.2)
        self.declare_parameter('max_box_size', 200)
        self.declare_parameter('model_dir', '')
        self.declare_parameter('yolo_model_path', '')
        self.declare_parameter('keras_model_path', '')
        self.declare_parameter('show_window', True)

        camera_topic = self.get_parameter('camera_topic').value
        result_topic = self.get_parameter('result_topic').value
        ready_topic = self.get_parameter('ready_topic').value
        self.confirmation_seconds = float(self.get_parameter('confirmation_seconds').value)
        self.green_ratio_threshold = float(self.get_parameter('green_ratio_threshold').value)
        self.square_ratio_min = float(self.get_parameter('square_ratio_min').value)
        self.square_ratio_max = float(self.get_parameter('square_ratio_max').value)
        self.max_box_size = int(self.get_parameter('max_box_size').value)
        configured_model_dir = str(self.get_parameter('model_dir').value).strip()
        env_model_dir = os.environ.get('DICE_GAME_MODEL_DIR', '').strip()
        model_dir = configured_model_dir or env_model_dir
        yolo_model_path = self.get_parameter('yolo_model_path').value
        keras_model_path = self.get_parameter('keras_model_path').value
        self.show_window = bool(self.get_parameter('show_window').value)

        if configured_model_dir:
            self.get_logger().info(f'Using model_dir from ROS parameter: {configured_model_dir}')
        elif env_model_dir:
            self.get_logger().info(f'Using model_dir from environment DICE_GAME_MODEL_DIR: {env_model_dir}')
        else:
            self.get_logger().warning(
                'model_dir is not set via ROS parameter or DICE_GAME_MODEL_DIR. '
                'Will try auto resolution from module path.'
            )

        try:
            resolved_yolo_path, resolved_keras_path = resolve_model_paths(
                module_dir=os.path.dirname(__file__),
                model_dir=model_dir,
                yolo_model_path=yolo_model_path,
                keras_model_path=keras_model_path,
            )
            self.yolo_model = YOLO(resolved_yolo_path)
            self.dice_classifier = tf.keras.models.load_model(resolved_keras_path)
            self.get_logger().info(
                f'Models loaded successfully: yolo={resolved_yolo_path}, keras={resolved_keras_path}'
            )
        except Exception as error:
            self.get_logger().error(f'Failed to load models: {error}')
            raise

        self.bridge = CvBridge()
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.dice_labels = ['1', '2', '3', '4', '5', '6']
        self.pending_result = None
        self.pending_result_since = None
        self.detection_enabled = True
        self.last_detected = None  # 이전 프레임의 탐지 결과 추적

        self.result_publisher = self.create_publisher(Int32, result_topic, 10)
        self.create_subscription(Image, camera_topic, self.image_callback, 10)
        self.create_subscription(Bool, ready_topic, self.ready_callback, 10)

        self.get_logger().info(f'Dice detector started. camera_topic={camera_topic}, result_topic={result_topic}')

    def ready_callback(self, msg):
        self.detection_enabled = bool(msg.data)
        if not self.detection_enabled:
            self.pending_result = None
            self.pending_result_since = None
            self.last_detected = None

    def get_square_crop(self, frame, x1, y1, x2, y2, target_size=(100, 100)):
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
        # 현재 상태 결정 (0=없음, 1-6=감지)
        current_state = detected_result if detected_result is not None else 0

        # 이전 상태와 현재 상태 비교
        if self.last_detected != current_state:
            # 상태 변경: 새로운 pending 설정
            self.pending_result = current_state
            self.pending_result_since = time.monotonic()
            self.last_detected = current_state
            state_desc = f'Dice appeared: {current_state}' if current_state > 0 else 'Dice disappeared'
            self.get_logger().info(f'{state_desc} (starting confirmation)')
            return

        # 이미 pending 중인 같은 상태인 경우
        now = time.monotonic()
        if self.pending_result_since is None:
            self.pending_result_since = now

        if (now - self.pending_result_since) >= self.confirmation_seconds:
            msg = Int32()
            msg.data = current_state
            self.result_publisher.publish(msg)
            action = f'Published dice result: {current_state}' if current_state > 0 else 'Published dice disappearance: 0'
            self.get_logger().info(action)
            self.pending_result = None
            self.pending_result_since = None

    def image_callback(self, msg):
        if not self.detection_enabled:
            return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            results = self.yolo_model(frame, verbose=False)[0]
        except Exception as error:
            self.get_logger().error(f'Failed to process frame: {error}')
            return

        best_result = None
        best_confidence = -1.0
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            bw, bh = x2 - x1, y2 - y1
            if bw <= 0 or bh <= 0:
                continue

            aspect_ratio = bw / bh
            roi_mask = green_mask[y1:y2, x1:x2]
            green_ratio = cv2.countNonZero(roi_mask) / float(bw * bh)

            if not (self.square_ratio_min <= aspect_ratio <= self.square_ratio_max):
                continue
            if bw >= self.max_box_size or bh >= self.max_box_size:
                continue
            if green_ratio < self.green_ratio_threshold:
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
            text = f'Dice: {eye_val} ({confidence * 100:.1f}%)'
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
            cv2.imshow('Turtlebot Dice Analysis', frame)
            cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DiceDetectorNode()
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
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

import cv2
import numpy as np
import rclpy
import os
import sys
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import tensorflow as tf

class DiceDetectorNode(Node):
    def __init__(self):
        super().__init__('dice_detector_node')
        
        # 1. 경로 설정 (스크립트 위치 기준 절대 경로 확보)
        # 이렇게 해야 어느 폴더에서 실행하든 모델 파일을 찾을 수 있어.
        package_path = os.path.dirname(os.path.abspath(__file__))
        yolo_path = os.path.join(package_path, 'yolov8n.pt')
        keras_path = os.path.join(package_path, 'green_dice_model.keras')

        # 2. 모델 로드
        try:
            self.yolo_model = YOLO(yolo_path)
            self.dice_classifier = tf.keras.models.load_model(keras_path)
            self.get_logger().info(f"Models loaded successfully from {package_path}")
        except Exception as e:
            self.get_logger().error(f"Failed to load models: {e}")
            sys.exit(1)

        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.dice_labels = ['1', '2', '3', '4', '5', '6']
        
        # 3. ROS2 설정
        self.bridge = CvBridge()
        # 터틀봇 카메라 네임스페이스(/camera)에 맞춰 토픽 수정
        self.subscription = self.create_subscription(
            Image, 
            '/camera/image_raw', 
            self.image_callback, 
            10)
        
        self.get_logger().info("Dice Detector Node Started - Subscribing to /camera/image_raw")

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
        if crop.size == 0: return None

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
        enhanced = self.clahe.apply(resized)
        
        input_arr = enhanced.astype('float32') / 255.0
        input_arr = np.expand_dims(input_arr, axis=(0, -1))
        return input_arr

    def image_callback(self, msg):
        # ROS 이미지를 OpenCV 이미지로 변환
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # YOLO 탐지 (주사위 영역 후보 찾기)
        results = self.yolo_model(frame, verbose=False)[0]
        
        # 초록색 주사위 필터링을 위한 HSV 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])  # 환경에 따라 값 미세조정 필요
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        for box in results.boxes:
            # 0번 클래스(일반적으로 YOLOv8에서 person이지만, 주사위 모델이라면 해당 클래스 인덱스 확인 필요)
            # 여기서는 모든 박스를 검사한 뒤 색상과 비율로 필터링하도록 유지
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            bw, bh = x2 - x1, y2 - y1
            if bw == 0 or bh == 0: continue

            aspect_ratio = bw / bh
            roi_mask = green_mask[y1:y2, x1:x2]
            
            # ROI 내 초록색 비율 계산
            green_ratio = cv2.countNonZero(roi_mask) / (bw * bh)

            # 필터링 조건: 정사각형에 가깝고, 너무 크지 않으며, 초록색 비중이 높을 때
            if (0.8 <= aspect_ratio <= 1.2) and (bw < 200 and bh < 200) and (green_ratio >= 0.4):
                input_data = self.get_square_crop(frame, x1, y1, x2, y2)
                if input_data is not None:
                    # Keras 분류기 예측
                    preds = self.dice_classifier.predict(input_data, verbose=0)
                    pred_class = np.argmax(preds)
                    confidence = preds[0][pred_class]
                    eye_val = self.dice_labels[pred_class]

                    # 시각화
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    text = f"Dice: {eye_val} ({confidence*100:.1f}%)"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('Turtlebot Dice Analysis', frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = DiceDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
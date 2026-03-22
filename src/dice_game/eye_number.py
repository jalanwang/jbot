import cv2
import numpy as np
import os
from ultralytics import YOLO
import tensorflow as tf

# 1. 모델 로드 (YOLOv8 + 사용자 학습 Keras 모델)
yolo_model = YOLO('yolov8n.pt')
dice_classifier = tf.keras.models.load_model('green_dice_model.keras')
print(f"Model Input Shape: {dice_classifier.input_shape}")

# 전처리를 위한 CLAHE 객체
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# 주사위 눈 레이블 (학습 시 설정한 순서대로 배치)
dice_labels = ['1', '2', '3', '4', '5', '6']

def get_square_crop(frame, x1, y1, x2, y2, target_size=(100, 100)):
    """비율 왜곡 없이 원본에서 정사각형 영역을 추출하여 전처리"""
    h_orig, w_orig = frame.shape[:2]
    bw, bh = x2 - x1, y2 - y1
    cx, cy = x1 + bw // 2, y1 + bh // 2
    
    # 300미만 제약은 루프에서 검사하므로 여기서는 긴 변 기준으로 정사각형 설정
    side = max(bw, bh)
    
    nx1 = max(0, cx - side // 2)
    ny1 = max(0, cy - side // 2)
    nx2 = nx1 + side
    ny2 = ny1 + side

    # 경계 보정 (정사각형 유지)
    if nx2 > w_orig:
        nx2 = w_orig
        nx1 = max(0, nx2 - side)
    if ny2 > h_orig:
        ny2 = h_orig
        ny1 = max(0, ny2 - side)

    crop = frame[ny1:ny2, nx1:nx2]
    if crop.size == 0: return None

    # 그레이스케일 변환 및 100x100 리사이즈
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
    enhanced = clahe.apply(resized)
    
    # 모델 입력 형태 (1, 100, 100, 1) 및 정규화
    input_arr = enhanced.astype('float32') / 255.0
    input_arr = np.expand_dims(input_arr, axis=(0, -1))
    return input_arr

# 2. 비디오 스트림 처리
cap = cv2.VideoCapture(3) # 카메라 인덱스 또는 비디오 파일 경로

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # YOLO 탐지
    results = yolo_model(frame, verbose=False)[0]
    
    # 녹색 필터링용 마스크 (실시간 어두운 환경 대응)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([25, 10, 5])
    upper_green = np.array([105, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    for box in results.boxes:
        # 박스 좌표 및 크기
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        bw, bh = x2 - x1, y2 - y1
        if bw == 0 or bh == 0: continue

        # --- 요청한 엄격한 조건 검사 ---
        # 1. 가로세로 비율 (0.75 ~ 1.25)
        aspect_ratio = bw / bh
        # 2. 박스 한쪽 길이 300 미만
        # 3. 녹색 비율 0.5 이상
        roi_mask = green_mask[y1:y2, x1:x2]
        green_ratio = cv2.countNonZero(roi_mask) / (bw * bh)

        if (0.75 <= aspect_ratio <= 1.25) and (bw < 300 and bh < 300) and (green_ratio >= 0.5):
            
            # 분류 모델 입력 전처리
            input_data = get_square_crop(frame, x1, y1, x2, y2)
            
            if input_data is not None:
                # Keras 모델 예측
                preds = dice_classifier.predict(input_data, verbose=0)
                pred_class = np.argmax(preds)
                confidence = preds[0][pred_class]
                eye_val = dice_labels[pred_class]

                # 시각화 (박스 및 눈 개수 표시)
                color = (0, 255, 0) # 녹색
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                text = f"Eye: {eye_val} ({confidence*100:.1f}%)"
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Green Dice Real-time Analysis', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
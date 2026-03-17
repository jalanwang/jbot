import cv2
import numpy as np
import os
from ultralytics import YOLO

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_IMAGES_DIR, resolve_model_file

def process_dice_with_yolo(input_dir=None,
                           output_dir=None,
                           model_path=None,
                           size=(100, 100)):
    """
    YOLO로 주사위 위치를 찾고, 해당 영역 내에서 컨투어를 추출하여 100x100으로 저장
    """
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_IMAGES_DIR)
    model_path = model_path or str(resolve_model_file('yolov8n.pt'))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. YOLO 모델 로드
    # 다이스를 학습시킨 모델이 없다면 일반 모델을 로드한 후 클래스 필터링 필요
    model = YOLO(model_path)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        img = cv2.imread(os.path.join(input_dir, filename))
        if img is None:
            continue

        h, w = img.shape[:2]

        # 2. YOLO 추론
        results = model(img, verbose=False)[0]

        # 탐지된 객체가 없을 경우 스킵
        if len(results.boxes) == 0:
            print(f"객체 미검출: {filename}")
            continue

        # 가장 신뢰도가 높은 첫 번째 객체 선택 (주사위가 하나라고 가정)
        box = results.boxes[0]
        xyxy = box.xyxy[0].cpu().numpy().astype(int)

        # YOLO 박스 좌표 (여유를 두기 위해 10% 정도 확장)
        margin = 20
        x1, y1 = max(0, xyxy[0] - margin), max(0, xyxy[1] - margin)
        x2, y2 = min(w, xyxy[2] + margin), min(h, xyxy[3] + margin)

        # YOLO 영역 크롭
        yolo_roi = img[y1:y2, x1:x2]
        roi_h, roi_w = yolo_roi.shape[:2]

        # 3. 크롭된 영역 내에서 컨투어 정밀 추출
        gray = cv2.cvtColor(yolo_roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            rx, ry, rw, rh = cv2.boundingRect(c)

            # 4. 패딩 및 정사각형 박싱
            padding_ratio = 1.2 # YOLO가 이미 영역을 좁혔으므로 패딩은 약간만
            side = int(max(rw, rh) * padding_ratio)
            side = min(side, roi_w, roi_h)

            rcx, rcy = rx + rw // 2, ry + rh // 2
            nx1 = max(0, rcx - side // 2)
            ny1 = max(0, rcy - side // 2)

            # ROI 경계 보정
            if nx1 + side > roi_w: nx1 = roi_w - side
            if ny1 + side > roi_h: ny1 = roi_h - side

            dice_crop = yolo_roi[ny1:ny1+side, nx1:nx1+side]
        else:
            dice_crop = yolo_roi

        if dice_crop.size == 0:
            continue

        # 5. 리사이즈 및 선명화 작업
        resized = cv2.resize(dice_crop, size, interpolation=cv2.INTER_CUBIC)

        # CLAHE (LAB 색공간 적용)
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_equalized = clahe.apply(l)
        lab_equalized = cv2.merge((l_equalized, a, b))
        equalized = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)

        # Unsharp Masking
        gaussian = cv2.GaussianBlur(equalized, (0, 0), 2.0)
        final_img = cv2.addWeighted(equalized, 1.5, gaussian, -0.5, 0)

        # 6. 저장
        cv2.imwrite(os.path.join(output_dir, filename), final_img)
        print(f"전처리 완료: {filename} (YOLO + Contour)")

if __name__ == "__main__":
    # YOLOv8 모델이 없다면 'yolov8n.pt'를 다운로드하여 기본 탐지를 수행해볼 수 있음
    # 실제 사용 시에는 주사위에 특화된 모델(.pt) 경로를 넣어야 해.
    process_dice_with_yolo()

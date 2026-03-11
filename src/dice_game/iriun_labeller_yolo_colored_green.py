import cv2
import numpy as np
import os
from ultralytics import YOLO

def process_green_dice_with_yolo(input_dir='./captured_images',
                               output_dir='./preprocessed_images',
                               model_path='yolov8n.pt', # 학습된 모델 경로로 수정
                               size=(100, 100)):
    """
    YOLO로 주사위 위치를 찾고, 해당 영역이 녹색인지 확인 후 100x100으로 저장
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 모델 로드 (파일 부재 대비 예외 처리)
    if not os.path.exists(model_path):
        print(f"경고: {model_path}를 찾을 수 없습니다. 기본 모델(yolov8n.pt)을 사용합니다.")
        model_path = 'yolov8n.pt'
    
    model = YOLO(model_path)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        img = cv2.imread(os.path.join(input_dir, filename))
        if img is None: continue

        h, w = img.shape[:2]

        # 2. 녹색 판별을 위한 HSV 변환 및 마스크 생성
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 녹색 범위 (조명 상황에 따라 H값 35~85 사이 조정 가능)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # 3. YOLO 추론
        results = model(img, verbose=False)[0]

        for box in results.boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy

            # --- 녹색 덩어리 검사 ---
            # 탐지된 박스 내부의 녹색 픽셀 수 계산
            roi_green_mask = green_mask[y1:y2, x1:x2]
            green_pixels = cv2.countNonZero(roi_green_mask)

            # 박스 면적 대비 녹색 비율이 너무 적으면 주사위가 아니라고 판단 (예: 배경)
            box_area = (x2 - x1) * (y2 - y1)
            if box_area == 0 or (green_pixels / box_area) < 0.2: # 녹색 비율 20% 미만 필터링
                continue

            # 4. 주사위 영역 크롭 및 정밀 컨투어 추출
            margin = 15
            mx1, my1 = max(0, x1 - margin), max(0, y1 - margin)
            mx2, my2 = min(w, x2 + margin), min(h, y2 + margin)
            yolo_roi = img[my1:my2, mx1:mx2]

            gray = cv2.cvtColor(yolo_roi, cv2.COLOR_BGR2GRAY)
            # 녹색 주사위는 배경과 대비가 클 것이므로 가우시안 블러 후 Otsu 이진화
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                c = max(contours, key=cv2.contourArea)
                rx, ry, rw, rh = cv2.boundingRect(c)
                side = int(max(rw, rh) * 1.2)
                
                # 중앙점 기준 정사각형 크롭
                rcx, rcy = rx + rw // 2, ry + rh // 2
                nx1 = max(0, rcx - side // 2)
                ny1 = max(0, rcy - side // 2)
                
                dice_crop = yolo_roi[ny1:ny1+side, nx1:nx1+side]
            else:
                dice_crop = yolo_roi

            if dice_crop.size == 0: continue

            # 5. 리사이즈 및 화질 개선
            resized = cv2.resize(dice_crop, size, interpolation=cv2.INTER_CUBIC)
            
            # CLAHE 적용
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_eq = clahe.apply(l)
            equalized = cv2.cvtColor(cv2.merge((l_eq, a, b)), cv2.COLOR_LAB2BGR)

            # 샤프닝 (Unsharp Masking)
            gauss = cv2.GaussianBlur(equalized, (0, 0), 2.0)
            final_img = cv2.addWeighted(equalized, 1.5, gauss, -0.5, 0)

            # 6. 저장
            save_path = os.path.join(output_dir, f"green_{filename}")
            cv2.imwrite(save_path, final_img)
            print(f"전처리 완료: {filename} (Green Dice Detected)")

if __name__ == "__main__":
    process_green_dice_with_yolo()
import cv2
import numpy as np
import os
from ultralytics import YOLO

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_IMAGES_DIR, resolve_model_file

def process_dice_strict_filter(input_dir=None,
                               output_dir=None,
                               size=(100, 100)):
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_IMAGES_DIR)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. YOLOv8n 모델 로드
    model = YOLO(str(resolve_model_file('yolov8n.pt')))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        src = cv2.imread(os.path.join(input_dir, filename))
        if src is None: continue
        h_orig, w_orig = src.shape[:2]

        # 2. YOLO 추론
        results = model(src, verbose=False)[0]

        # 3. 어두운 녹색 대응 HSV 마스크
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        lower_green = np.array([25, 10, 5])
        upper_green = np.array([105, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        idx = 0
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            bw, bh = x2 - x1, y2 - y1

            if bw == 0 or bh == 0: continue

            # --- 필터 1: 가로세로 비율 (0.75 ~ 1.25) ---
            aspect_ratio = bw / bh
            if not (0.75 <= aspect_ratio <= 1.25):
                continue

            # --- 필터 2: 박스의 한쪽 길이는 300 미만 ---
            if bw >= 300 or bh >= 300:
                continue

            # --- 필터 3: 박스 내 녹색 비율 (0.5 이상) ---
            roi_mask = green_mask[y1:y2, x1:x2]
            green_ratio = cv2.countNonZero(roi_mask) / (bw * bh)
            if green_ratio < 0.5:
                continue

            # --- 정사각형 영역 계산 및 비율 유지 추출 ---
            cx, cy = x1 + bw // 2, y1 + bh // 2
            side = max(bw, bh) # 긴 변 기준

            # 이미지 경계를 벗어나지 않도록 좌표 클램핑 (정사각형 유지)
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

            # 정사각형 크롭 및 변환
            dice_square_crop = src[ny1:ny2, nx1:nx2]
            gray = cv2.cvtColor(dice_square_crop, cv2.COLOR_BGR2GRAY)

            # 최종 리사이즈 및 선명화
            final_res = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)
            final_res = clahe.apply(final_res)

            # 4. 저장
            save_name = f"strict_dice_{idx}_{filename}"
            cv2.imwrite(os.path.join(output_dir, save_name), final_res)
            print(f"추출: {save_name} | Ratio: {aspect_ratio:.2f} | Green: {green_ratio:.2f} | MaxSide: {side}")
            idx += 1

if __name__ == "__main__":
    process_dice_strict_filter()

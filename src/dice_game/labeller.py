import cv2
import numpy as np
import os

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_DIR

def process_center_dice(input_dir=None, output_dir=None, size=(100, 100)):
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_DIR)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')): continue

        img = cv2.imread(os.path.join(input_dir, filename))
        if img is None: continue

        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2

        # 1. 중앙 관심 영역(ROI) 설정 (너무 넓으면 배경에 간섭받으므로 적절히 설정)
        roi_gap = 250 # 중앙에서 상하좌우 250px, 총 500x500 영역 탐색
        x1, y1 = max(0, cx - roi_gap), max(0, cy - roi_gap)
        x2, y2 = min(w, cx + roi_gap), min(h, cy + roi_gap)
        roi = img[y1:y2, x1:x2]

        # 2. 이미지 이진화 및 컨투어 검출 (주사위 윤곽 잡기)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 중앙부에서 가장 큰 컨투어를 주사위로 간주
            c = max(contours, key=cv2.contourArea)
            rx, ry, rw, rh = cv2.boundingRect(c)

            # 3. 정사각형 박싱 및 패딩 로직
            max_l = max(rw, rh)
            # 주사위 중심 좌표 (ROI 기준)
            rcx, rcy = rx + rw // 2, ry + rh // 2

            # 정사각형 크롭 영역 계산
            nx1 = max(0, rcx - max_l // 2)
            ny1 = max(0, rcy - max_l // 2)

            dice_crop = roi[ny1:ny1+max_l, nx1:nx1+max_l]

            # 4. 100x100 리사이즈
            final_dice = cv2.resize(dice_crop, size, interpolation=cv2.INTER_AREA)

            cv2.imwrite(os.path.join(output_dir, filename), final_dice)
            print(f"성공: {filename}")
        else:
            print(f"실패(객체 없음): {filename}")

if __name__ == '__main__':
    process_center_dice()

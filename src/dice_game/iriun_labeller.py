import cv2
import numpy as np
import os

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_IMAGES_DIR

def process_center_dice_sharp(input_dir=None, output_dir=None, size=(100, 100)):
    """
    Iriun에서 캡처된 고해상도(1280x720) 이미지의 정중앙 ROI 영역을 추출하여
    히스토그램 보정(CLAHE)과 샤프닝을 적용하고 100x100으로 저장하는 함수
    """
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_IMAGES_DIR)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # CLAHE 객체 생성 (대비 제한 2.0, 그리드 크기 8x8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        img = cv2.imread(os.path.join(input_dir, filename))
        if img is None:
            continue

        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2

        # 1. ROI 설정 (1280x720 해상도에 맞춰 탐색 범위 확장)
        # 720p 해상도에서는 주사위가 더 크게 찍히므로 탐색 범위를 400x400으로 확장
        roi_half_side = 200
        x1, y1 = max(0, cx - roi_half_side), max(0, cy - roi_half_side)
        x2, y2 = min(w, cx + roi_half_side), min(h, cy + roi_half_side)
        roi = img[y1:y2, x1:x2]

        roi_h, roi_w = roi.shape[:2]

        # 2. 전처리 (그레이스케일 -> 블러 -> 이진화)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 해상도가 높아졌으므로 유효 컨투어 면적 기준을 800으로 상향
            valid_contours = [c for c in contours if cv2.contourArea(c) > 800]
            if not valid_contours:
                dice_crop = roi
            else:
                c = max(valid_contours, key=cv2.contourArea)
                rx, ry, rw, rh = cv2.boundingRect(c)

                # 3. 패딩 추가 및 정사각형 박싱 (기존 1.4배 유지)
                padding_ratio = 1.4
                side = int(max(rw, rh) * padding_ratio)
                side = min(side, roi_w, roi_h)

                rcx, rcy = rx + rw // 2, ry + rh // 2
                nx1 = max(0, rcx - side // 2)
                ny1 = max(0, rcy - side // 2)

                if nx1 + side > roi_w: nx1 = roi_w - side
                if ny1 + side > roi_h: ny1 = roi_h - side

                nx2, ny2 = nx1 + side, ny1 + side
                dice_crop = roi[ny1:ny2, nx1:nx2]
        else:
            dice_crop = roi

        if dice_crop.size == 0:
            continue

        # 4. 리사이즈 (100x100 고정)
        resized_dice = cv2.resize(dice_crop, size, interpolation=cv2.INTER_CUBIC)

        # 5. 히스토그램 보정 (CLAHE)
        lab = cv2.cvtColor(resized_dice, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_equalized = clahe.apply(l)
        lab_equalized = cv2.merge((l_equalized, a, b))
        equalized_dice = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)

        # 6. 샤프닝 보정 (언샤프 마스크)
        gaussian = cv2.GaussianBlur(equalized_dice, (0, 0), 2.0)
        final_dice = cv2.addWeighted(equalized_dice, 1.5, gaussian, -0.5, 0)

        # 7. 파일 저장
        cv2.imwrite(os.path.join(output_dir, filename), final_dice)
        print(f"작업 완료: {filename} (Input: {w}x{h} -> Output: 100x100)")

if __name__ == "__main__":
    process_center_dice_sharp()

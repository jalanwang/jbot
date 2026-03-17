import cv2
import numpy as np
import os
from ultralytics import YOLO

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_IMAGES_DIR, resolve_model_file

def process_green_dice_512_gray(input_dir=None,
                                output_dir=None,
                                size=(100, 100)):
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_IMAGES_DIR)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. yolov8n.pt 로드
    model = YOLO(str(resolve_model_file('yolov8n.pt')))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    # ROI 설정 (중앙 512x512)
    ROI_SIZE = 512

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        full_img = cv2.imread(os.path.join(input_dir, filename))
        if full_img is None: continue

        h, w = full_img.shape[:2]

        # --- 2. 중앙 512x512 ROI 추출 ---
        cx, cy = w // 2, h // 2
        rx1, ry1 = cx - ROI_SIZE // 2, cy - ROI_SIZE // 2
        rx2, ry2 = cx + ROI_SIZE // 2, cy + ROI_SIZE // 2

        # 이미지 경계 처리 (512보다 작을 경우 대비)
        rx1, ry1 = max(0, rx1), max(0, ry1)
        rx2, ry2 = min(w, rx2), min(h, ry2)

        roi_img = full_img[ry1:ry2, rx1:rx2].copy()
        roi_h, roi_w = roi_img.shape[:2]

        # --- 3. 녹색 마스크 생성 (컬러 기반) ---
        hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([90, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # --- 4. YOLOv8n 추론 (ROI 영역 내에서만) ---
        results = model(roi_img, verbose=False)[0]

        for i, box in enumerate(results.boxes):
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            bx1, by1, bx2, by2 = xyxy

            # 녹색 덩어리 확인 필터
            target_mask = green_mask[by1:by2, bx1:bx2]
            if target_mask.size == 0 or cv2.countNonZero(target_mask) < 100:
                continue

            # --- 5. 주사위 정밀 크롭 및 그레이스케일 변환 ---
            margin = 10
            x1, y1 = max(0, bx1 - margin), max(0, by1 - margin)
            x2, y2 = min(roi_w, bx2 + margin), min(roi_h, by2 + margin)
            dice_roi = roi_img[y1:y2, x1:x2]

            # 컨투어 추출
            gray_roi = cv2.cvtColor(dice_roi, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray_roi, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if cnts:
                c = max(cnts, key=cv2.contourArea)
                rx, ry, rw, rh = cv2.boundingRect(c)
                side = int(max(rw, rh) * 1.2)
                rcx, rcy = rx + rw // 2, ry + rh // 2
                nx1, ny1 = max(0, rcx - side // 2), max(0, rcy - side // 2)
                final_crop = dice_roi[ny1:ny1+side, nx1:nx1+side]
            else:
                final_crop = dice_roi

            if final_crop.size == 0: continue

            # 리사이즈 및 그레이스케일 최종 처리
            resized = cv2.resize(final_crop, size, interpolation=cv2.INTER_CUBIC)
            gray_res = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

            # CLAHE 및 선명화
            gray_res = clahe.apply(gray_res)
            gauss = cv2.GaussianBlur(gray_res, (0, 0), 2.0)
            final_img = cv2.addWeighted(gray_res, 1.5, gauss, -0.5, 0)

            # 저장
            save_name = f"c512_gray_{i}_{filename}"
            cv2.imwrite(os.path.join(output_dir, save_name), final_img)
            print(f"중앙 512 ROI에서 추출 성공: {save_name}")

if __name__ == "__main__":
    process_green_dice_512_gray()

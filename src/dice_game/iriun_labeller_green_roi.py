import cv2
import numpy as np
import os

from project_paths import CAPTURED_IMAGES_DIR, PREPROCESSED_IMAGES_DIR

def crop_enhanced_green_lumps(input_dir=None,
                               output_dir=None,
                               size=(100, 100)):
    input_dir = input_dir or str(CAPTURED_IMAGES_DIR)
    output_dir = output_dir or str(PREPROCESSED_IMAGES_DIR)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # CLAHE 객체 생성 (명암 보정용)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    ROI_SIZE = 512

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        src = cv2.imread(os.path.join(input_dir, filename))
        if src is None: continue
        h, w = src.shape[:2]

        # 1. 중앙 512x512 ROI 추출
        cx, cy = w // 2, h // 2
        x1, y1 = max(0, cx - ROI_SIZE // 2), max(0, cy - ROI_SIZE // 2)
        x2, y2 = min(w, cx + ROI_SIZE // 2), min(h, cy + ROI_SIZE // 2)
        roi = src[y1:y2, x1:x2].copy()

        # 2. 명암 보정 (LAB 색공간 활용)
        # 어두운 환경에서도 녹색을 잘 찾기 위해 L(밝기) 채널 강제 보정
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_enhanced = clahe.apply(l)
        roi_enhanced = cv2.cvtColor(cv2.merge((l_enhanced, a, b)), cv2.COLOR_LAB2BGR)

        # 3. 보정된 이미지로 HSV 마스크 생성 (어두운 녹색 타겟)
        hsv = cv2.cvtColor(roi_enhanced, cv2.COLOR_BGR2HSV)
        # V(밝기) 하한선을 20으로 낮추고, S(채도) 범위를 넓힘
        lower_green = np.array([30, 25, 20])
        upper_green = np.array([95, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # 4. 컨투어 추출 (덩어리 찾기)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for i, cnt in enumerate(contours):
            if cv2.contourArea(cnt) < 500: # 최소 면적 필터링
                continue

            # 5. 패딩 없이 딱 맞게 바운딩 박스 추출
            bx, by, bw, bh = cv2.boundingRect(cnt)

            # 보정 전 원본 ROI 혹은 보정본에서 크롭 (학습용은 보정본 추천)
            lump_crop = roi_enhanced[by:by+bh, bx:bx+bw]

            # 6. 최종 그레이스케일 변환 및 저장
            gray = cv2.cvtColor(lump_crop, cv2.COLOR_BGR2GRAY)

            # 100x100 리사이즈 (규격화)
            resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)

            # 저장 전 한 번 더 선명화
            final_equalized = clahe.apply(resized)
            blur = cv2.GaussianBlur(final_equalized, (0, 0), 1.0)
            final_img = cv2.addWeighted(final_equalized, 1.5, blur, -0.5, 0)

            # 저장
            save_name = f"enhanced_lump_{i}_{filename}"
            cv2.imwrite(os.path.join(output_dir, save_name), final_img)
            print(f"추출 완료: {save_name}")

if __name__ == "__main__":
    crop_enhanced_green_lumps()

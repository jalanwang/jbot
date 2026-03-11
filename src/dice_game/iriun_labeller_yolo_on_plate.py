import cv2
import numpy as np
import os
from ultralytics import YOLO

def process_dice_on_purple_pad(input_dir='./captured_images',
                               output_dir='./preprocessed_images',
                               model_path='yolov8n.pt', # 알반 모델 경로
                               size=(100, 100)):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    model = YOLO(model_path)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        img = cv2.imread(os.path.join(input_dir, filename))
        if img is None: continue

        h, w = img.shape[:2]

        # 1. 보라색 판 영역 마스크 생성 (HSV 활용)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 보라색 범위 설정 (조명에 따라 조정 필요)
        lower_purple = np.array([130, 50, 50])
        upper_purple = np.array([165, 255, 255])
        purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)

        # 2. YOLO 추론
        results = model(img, verbose=False)[0]

        for box in results.boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy

            # --- 필터링: 바운딩 박스 내부에 보라색이 있는지 확인 ---
            # 박스 내부의 마스크 영역만 슬라이싱
            roi_mask = purple_mask[y1:y2, x1:x2]
            
            # 보라색 픽셀 비율 계산 (주사위가 판 위에 있다면 테두리 근처에 보라색이 잡힘)
            # 혹은 박스 하단부나 주변부 픽셀을 체크
            purple_pixel_count = cv2.countNonZero(roi_mask)
            
            # 보라색 픽셀이 거의 없다면 보라판 밖의 주사위로 간주하고 무시
            if purple_pixel_count < 50: # 최소 50픽셀 이상 보라색이 검출되어야 함
                continue

            # 3. 유효한 주사위 영역 크롭 (여유 마진 적용)
            margin = 15
            mx1, my1 = max(0, x1 - margin), max(0, y1 - margin)
            mx2, my2 = min(w, x2 + margin), min(h, y2 + margin)
            dice_roi = img[my1:my2, mx1:mx2]

            # 4. 정밀 추출 및 전처리
            gray = cv2.cvtColor(dice_roi, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                c = max(contours, key=cv2.contourArea)
                rx, ry, rw, rh = cv2.boundingRect(c)
                side = int(max(rw, rh) * 1.2)
                rcx, rcy = rx + rw // 2, ry + rh // 2
                
                # 정사각형 크롭 좌표 계산
                nx1 = max(0, rcx - side // 2)
                ny1 = max(0, rcy - side // 2)
                final_crop = dice_roi[ny1:ny1+side, nx1:nx1+side]
            else:
                final_crop = dice_roi

            if final_crop.size == 0: continue

            # 5. 리사이즈 및 선명화 (기존 로직 유지)
            resized = cv2.resize(final_crop, size, interpolation=cv2.INTER_CUBIC)
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_eq = clahe.apply(l)
            equalized = cv2.cvtColor(cv2.merge((l_eq, a, b)), cv2.COLOR_LAB2BGR)
            
            # 샤프닝
            gauss = cv2.GaussianBlur(equalized, (0, 0), 2.0)
            sharpened = cv2.addWeighted(equalized, 1.5, gauss, -0.5, 0)

            # 저장 (파일명 중복 방지를 위해 인덱스 추가 가능)
            save_name = f"purple_{filename}"
            cv2.imwrite(os.path.join(output_dir, save_name), sharpened)
            print(f"보라판 주사위 저장 완료: {save_name}")

if __name__ == "__main__":
    process_dice_on_purple_pad()
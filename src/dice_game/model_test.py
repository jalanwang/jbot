import numpy as np
from PIL import Image
from tensorflow import keras
import os

# 1. 학습된 모델 로드
MODEL_PATH = "dice_model.keras"
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: {MODEL_PATH} 파일이 없습니다. 먼저 학습을 완료하세요.")
    exit()

model = keras.models.load_model(MODEL_PATH)

# 2. 클래스 라벨 (DataReader와 동일한 순서)
labels = ["1", "2", "3", "4", "5", "6"]

# 모델의 입력 사이즈 자동 추출
input_h, input_w = model.input_shape[1:3]

def predict_dice(img_path):
    try:
        # 이미지 로드 및 전처리
        img_raw = Image.open(img_path).convert("RGB")
        img_resized = img_raw.resize((input_w, input_h))

        img_array = np.asarray(img_resized) / 255.0
        img_input = np.expand_dims(img_array, axis=0)

        # 예측 실행
        predictions = model.predict(img_input, verbose=0)
        result_idx = np.argmax(predictions[0])
        confidence = predictions[0][result_idx]
        label_text = labels[result_idx]

        print(f"파일: {os.path.basename(img_path):<20} | 예측: {label_text}개 | 확신도: {confidence*100:.2f}%")
    except Exception as e:
        print(f"파일 처리 중 오류 발생 ({img_path}): {e}")

# 3. 폴더 내 모든 사진 검증
test_folder = "./test_images"

if os.path.exists(test_folder):
    print(f"\n--- {test_folder} 내 이미지 검증 시작 ---")
    files = [f for f in os.listdir(test_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not files:
        print("검증할 이미지 파일이 폴더에 없습니다.")
    else:
        for f in sorted(files):
            full_path = os.path.join(test_folder, f)
            predict_dice(full_path)
    print("\n--- 모든 검증 완료 ---")
else:
    # 아래 줄 끝에 불필요한 기호가 들어가지 않도록 주의해
    print(f"ERROR: '{test_folder}' 폴더를 찾을 수 없습니다.")

from tensorflow import keras
import data_reader
import numpy as np

# 1. 데이터 읽기
dr = data_reader.DataReader()

# DataReader가 컬러(3채널)로 읽어온 데이터를 1채널로 변환
if dr.train_X.shape[-1] == 3:
    # 단순 평균(np.mean)보다 공식적인 Grayscale 변환 비율(Luma)을 적용하는 것이 더 정확함
    dr.train_X = (0.299 * dr.train_X[:,:,:,0] + 0.587 * dr.train_X[:,:,:,1] + 0.114 * dr.train_X[:,:,:,2])
    dr.test_X = (0.299 * dr.test_X[:,:,:,0] + 0.587 * dr.test_X[:,:,:,1] + 0.114 * dr.test_X[:,:,:,2])
    
    # Keras 입력 규격을 위해 마지막에 1채널 차원 추가 (N, 100, 100, 1)
    dr.train_X = np.expand_dims(dr.train_X, axis=-1)
    dr.test_X = np.expand_dims(dr.test_X, axis=-1)

print(f"변환 후 데이터 Shape: {dr.train_X.shape}") # (259, 100, 100, 1) 확인

EPOCHS = 50

# 2. 인공신경망 제작 (1채널 입력 설정)
model = keras.Sequential([
    # input_shape를 (100, 100, 1)로 수정하여 1채널 모델임을 명시
    keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(100, 100, 1)),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Conv2D(64, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Conv2D(64, (3, 3), activation='relu'), # 레이어 하나 더 추가하면 정교함 상승
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.2), # 과적합 방지를 위한 드롭아웃 추가
    keras.layers.Dense(6, activation='softmax')
])

model.compile(optimizer='adam',
              metrics=['accuracy'],
              loss='sparse_categorical_crossentropy')

print(f"Model Input Shape: {model.input_shape}")
print("\n--- 1채널 기반 학습 시작 ---")

history = model.fit(dr.train_X, dr.train_Y, 
                    epochs=EPOCHS,
                    validation_data=(dr.test_X, dr.test_Y))

# 3. 모델 저장
model.save("green_dice_model.keras")
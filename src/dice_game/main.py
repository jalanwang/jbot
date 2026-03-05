from tensorflow import keras
import data_reader

EPOCHS = 50 # 주사위 눈은 정교하므로 에포크를 조금 더 늘림
dr = data_reader.DataReader()

model = keras.Sequential([
    # 첫 번째 레이어: 입력 사이즈 100x100x3
    keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(100, 100, 3)),
    keras.layers.MaxPooling2D((2, 2)),
    
    keras.layers.Conv2D(64, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D((2, 2)),
    
    keras.layers.Conv2D(128, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D((2, 2)),
    
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.3), # 과적합 방지
    # 최종 출력: 6개 클래스 (1~6), 다중 분류를 위한 softmax
    keras.layers.Dense(6, activation='softmax') 
])

model.compile(optimizer='adam', 
              metrics=['accuracy'],
              loss='sparse_categorical_crossentropy')

print("\n--- 학습 시작 ---")
history = model.fit(dr.train_X, dr.train_Y, epochs=EPOCHS, 
                    validation_data=(dr.test_X, dr.test_Y))

# 모델 저장
model.save("dice_model.keras")

from tensorflow import keras
import data_reader

EPOCHS = 50 # 주사위 눈은 정교하므로 에포크를 조금 더 늘림
dr = data_reader.DataReader()

# 인공신경망 제작 부분
model = keras.Sequential([
    keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(100, 100, 3)),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Conv2D(64, (3, 3), activation='relu'),
    keras.layers.MaxPooling2D((2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation='relu'),
    # 주사위 눈 1~6을 분류하기 위해 6으로 설정
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
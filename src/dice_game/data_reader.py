import os
import numpy as np
from PIL import Image
import random

from project_paths import CLASSIFIED_DATA_DIR

class DataReader():
    def __init__(self, data_dir=None, image_size=(100, 100), train_split=0.8):
        # 주사위 눈 1개부터 6개까지 클래스 설정
        self.label = ["1", "2", "3", "4", "5", "6"]
        self.train_X, self.train_Y = [], []
        self.test_X, self.test_Y = [], []
        self.data_dir = data_dir or str(CLASSIFIED_DATA_DIR)
        self.image_size = image_size
        self.train_split = train_split
        self.read_images()

    def read_images(self):
        data = []
        # 분류 학습용 폴더 안에 '1', '2'...'6' 이라는 이름의 폴더가 있어야 함
        for i, cls in enumerate(self.label):
            path = os.path.join(self.data_dir, cls)
            if not os.path.exists(path): continue
            for el in os.listdir(path):
                img = Image.open(os.path.join(path, el)).convert("RGB")
                # 앞서 정규화한 100x100 사이즈로 로드
                img = img.resize(self.image_size)
                data.append((np.asarray(img), i))
                img.close()

        if not data:
            raise RuntimeError(
                f"No training images found in '{self.data_dir}'. "
                "Expected class folders: 1,2,3,4,5,6"
            )

        random.shuffle(data)

        # 8:2 비율로 분할
        split = int(len(data) * self.train_split)
        train_data = data[:split]
        test_data = data[split:]

        self.train_X = np.asarray([d[0] for d in train_data]) / 255.0
        self.train_Y = np.asarray([d[1] for d in train_data])
        self.test_X = np.asarray([d[0] for d in test_data]) / 255.0
        self.test_Y = np.asarray([d[1] for d in test_data])

        print(f"Data Read Done from {self.data_dir}! Training: {self.train_X.shape}, Test: {self.test_X.shape}")

import os
import numpy as np
from PIL import Image
import random

class DataReader():
    def __init__(self):
        # 주사위 눈 1개부터 6개까지 클래스 설정
        self.label = ["1", "2", "3", "4", "5", "6"]
        self.train_X, self.train_Y = [], []
        self.test_X, self.test_Y = [], []
        self.read_images()

    def read_images(self):
        data = []
        # ./data 폴더 안에 '1', '2'...'6' 이라는 이름의 폴더가 있어야 함
        for i, cls in enumerate(self.label):
            path = "data/" + cls
            if not os.path.exists(path): continue
            for el in os.listdir(path):
                img = Image.open(path + "/" + el).convert("RGB")
                # 앞서 정규화한 100x100 사이즈로 로드
                img = img.resize((100, 100))
                data.append((np.asarray(img), i))
                img.close()

        random.shuffle(data)

        # 8:2 비율로 분할
        split = int(len(data) * 0.8)
        train_data = data[:split]
        test_data = data[split:]

        self.train_X = np.asarray([d[0] for d in train_data]) / 255.0
        self.train_Y = np.asarray([d[1] for d in train_data])
        self.test_X = np.asarray([d[0] for d in test_data]) / 255.0
        self.test_Y = np.asarray([d[1] for d in test_data])

        print(f"Data Read Done! Training: {self.train_X.shape}, Test: {self.test_X.shape}")
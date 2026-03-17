from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QFile
import os

class CameraWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 현재 파이썬 파일이 있는 폴더 경로를 가져옴
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # UI 파일의 절대 경로 생성
        ui_path = os.path.join(current_dir, "yolo_window.ui")

        # 1. UI 파일 로드
        loader = QUiLoader()
        file = QFile(ui_path)
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.setWindowTitle("YOLO Real-time Detection")

    def update_image(self, q_pixmap):
        # 2. 메인 창에서 받은 이미지를 레이블에 출력
        self.ui.label_yolo_view.setPixmap(q_pixmap)


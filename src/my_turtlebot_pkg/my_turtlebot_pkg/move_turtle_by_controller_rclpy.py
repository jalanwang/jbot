# ~/robot/robot_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/my_package/move_turtle_by_controller_rclpy.py

# PySide6를 이용하여 GUI로 키보드 입력을 받아 터틀봇을 움직이는 노드.
# controller.ui가 설계도, controller_ui.py가 설계도를 바탕으로 생성된 GUI 클래스.
# move_turtle_by_controller_rclpy.py에서는 controller_ui.py에서 생성된 GUI 클래스를 사용하여
# GUI 이벤트 핸들러에서 ROS2 퍼블리셔를 통해 터틀봇을 제어하는 노드를 구현.

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
# controller_ui.py에서 Ui_MainWindow 클래스를 import.
from .controller_ui import Ui_MainWindow

from my_turtlebot_pkg.move_turtle_logic import MoveTurtleLogic # 움직임을 담당하는 엔진 클래스

import rclpy
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import QTimer, Qt

class MainWindow(QMainWindow):
  def __init__(self, logic_engine):
    super(MainWindow, self).__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self) # setupUi 함수를 호출해 MainWindow에 있는 위젯을 배치한다.
    self.logic_engine = logic_engine

    # button clicked 이벤트 핸들러로 button_clicked 함수와 연결한다.
    self.ui.pb_go.clicked.connect(self.pb_go_clicked)
    self.ui.pb_left.clicked.connect(self.pb_left_clicked)
    self.ui.pb_stop.clicked.connect(self.pb_stop_clicked)
    self.ui.pb_right.clicked.connect(self.pb_right_clicked)
    self.ui.pb_back.clicked.connect(self.pb_back_clicked)

    self.ui.pb_triangle.clicked.connect(self.pb_triangle_clicked)
    self.ui.pb_square.clicked.connect(self.pb_square_clicked)

    self.time = QTimer(self)
    self.time.timeout.connect(self.ros_main_loop)
    self.time.start(50) # 50ms마다 ros_main_loop 함수를 호출하여 ROS2 이벤트를 처리한다.

  def pb_go_clicked(self): self.logic_engine.update_key('w')
  def pb_back_clicked(self): self.logic_engine.update_key('x')
  def pb_left_clicked(self): self.logic_engine.update_key('a')
  def pb_right_clicked(self): self.logic_engine.update_key('d')
  def pb_stop_clicked(self): self.logic_engine.update_key('s')

  def pb_triangle_clicked(self): self.logic_engine.action_triangle()
  def pb_square_clicked(self): self.logic_engine.action_square()

  def keyPressEvent(self, event: QKeyEvent):
    """키보드 입력 이벤트 처리는 이 함수에서 처리한다."""
    key_map = {
      Qt.Key_W: 'w',
      Qt.Key_X: 'x',
      Qt.Key_A: 'a',
      Qt.Key_D: 'd',
      Qt.Key_S: 's',
      Qt.Key_1: 'triangle', # 숫자 1키
      Qt.Key_2: 'square'    # 숫자 2키
    }
    ros_key = key_map.get(event.key())
    if ros_key:
      if ros_key == 'triangle': self.logic_engine.action_triangle('1')
      elif ros_key == 'square': self.logic_engine.action_square('2')
      else: self.logic_engine.update_key(ros_key)

  def ros_main_loop(self):
    rclpy.spin_once(self.logic_engine, timeout_sec=0)
    self.logic_engine.update_and_publish() # 로직 엔진의 update_and_publish 함수를 호출하여 로직을 업데이트하고 cmd_vel 메시지를 발행한다.

def main(args=None):
    rclpy.init(args=args)

    logic_engine = MoveTurtleLogic() # 움직임을 담당하는 엔진 하나 생성.

    # GUI 앱 실행 및 엔진 주입
    app = QApplication(sys.argv)
    window = MainWindow(logic_engine) # GUI 창에 로직 엔진을 주입하여 이벤트 핸들러에서 사용할 수 있도록 함
    window.show()

    try:
      sys.exit(app.exec())
    except KeyboardInterrupt:
      pass
    finally:
      rclpy.shutdown()

# 이 부분이 반드시 있어야 합니다!
if __name__ == "__main__":
    main()

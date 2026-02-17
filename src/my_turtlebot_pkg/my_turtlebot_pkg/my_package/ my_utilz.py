# ~/robot/robot_ws/src/my_turtlebot_pkg/my_turtlebot_pkg/my_contents.py

import os
import select
import sys
import termios
import tty

class KeyParser:
    def __init__(self):
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8')

        tty.setraw(sys.stdin.fileno())
        # 0.1초 동안 입력을 대기
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

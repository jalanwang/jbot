import numpy as np
from nav_msgs.msg import Odometry

class TurtlebotPose:
    def __init__(self, node):
        self.node = node
        self.last_pose_x = 0.0
        self.last_pose_y = 0.0
        self.last_pose_theta = 0.0
        self.init_odom_state = False

        # 부모 노드의 인스턴스를 사용하여 구독자 생성
        self.odom_sub = self.node.create_subscription(
            Odometry, 'odom', self.odom_callback, 10)

    def odom_callback(self, msg):
        self.last_pose_x = msg.pose.pose.position.x
        self.last_pose_y = msg.pose.pose.position.y

        # 쿼터니언을 오일러 각도(Yaw)로 변환
        _, _, self.last_pose_theta = self.euler_from_quaternion(msg.pose.pose.orientation)
        self.init_odom_state = True

    def euler_from_quaternion(self, quat):
        """사원수를 받아 Roll, Pitch, Yaw(Theta) 반환"""
        x, y, z, w = quat.x, quat.y, quat.z, quat.w

        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        # Yaw (z-axis rotation) - 터틀봇에게 가장 중요한 값
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

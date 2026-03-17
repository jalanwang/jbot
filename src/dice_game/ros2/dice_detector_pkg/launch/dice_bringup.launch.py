import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    detector_share = get_package_share_directory('dice_detector_pkg')
    motion_share = get_package_share_directory('dice_motion_pkg')

    detector_params = os.path.join(detector_share, 'config', 'dice_detector.params.yaml')
    motion_params = os.path.join(motion_share, 'config', 'dice_motion.params.yaml')

    return LaunchDescription([
        Node(
            package='dice_detector_pkg',
            executable='dice_detector',
            name='dice_detector',
            output='screen',
            parameters=[detector_params],
        ),
        Node(
            package='dice_motion_pkg',
            executable='dice_motion',
            name='dice_motion',
            output='screen',
            parameters=[motion_params],
        ),
    ])

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('dice_motion_pkg')
    params_file = os.path.join(package_share, 'config', 'dice_motion.params.yaml')

    return LaunchDescription([
        Node(
            package='dice_motion_pkg',
            executable='dice_motion',
            name='dice_motion',
            output='screen',
            parameters=[params_file],
        ),
    ])

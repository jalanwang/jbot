import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'my_turtlebot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all Python files in the my_turtlebot_pkg directory
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # 내 패키지 디렉토리 내 my_package 폴더내의 모든 Python 파일을 포함하도록 수정
        (os.path.join('share', package_name, 'my_package'), glob('my_package/*.py')),
    ],
    install_requires=['setuptools', 'PySide6'], # PySide6 패키지에 대한 의존성 추가

    zip_safe=True,
    maintainer='robot',
    maintainer_email='jalanwang@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
          'move_turtle_pub = my_turtlebot_pkg.move_turtle_pub:main',
          'move_turtle_pub_adv = my_turtlebot_pkg.move_turtle_pub_adv:main',
          'lidar_subscriber = my_turtlebot_pkg.lidar_subscriber:main',
          'detect_obstacle = my_turtlebot_pkg.detect_obstacle:main',
          'detect_obstacle_aperature = my_turtlebot_pkg.detect_obstacle_aperature:main',
          'move_turtle_with_detecting_obstacle = my_turtlebot_pkg.move_turtle_with_detecting_obstacle:main',
          'move_turtle_by_controller = my_turtlebot_pkg.move_turtle_by_controller:main',
          'move_turtle_by_controller_rclpy = my_turtlebot_pkg.move_turtle_by_controller_rclpy:main',

        ],
    },
)

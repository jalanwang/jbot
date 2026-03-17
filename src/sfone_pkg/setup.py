from setuptools import find_packages, setup

package_name = 'sfone_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    package_data={
        package_name: ['*.ui', '*.pt'],
    },
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['sfone_pkg/turtlebot_controller.ui']), # UI 파일 추가
        ('share/' + package_name, ['sfone_pkg/yolo_window.ui']),        # UI 파일 추가
    ],
    install_requires=[
        'setuptools',
        'PySide6',
        'ultralytics',
        'opencv-python',
        'pygame',
        'gTTS',
    ],
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
        'auto_drive = sfone_pkg.my_auto_drive:main',
        'yolo_node = sfone_pkg.my_turtle_yolo:main',
        'my_turtlebot_controller = sfone_pkg.my_turtlebot_controller:main',
        ],
    },
)

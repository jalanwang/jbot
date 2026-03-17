import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'dice_detector_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools', 'numpy', 'opencv-python', 'ultralytics', 'tensorflow'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='jalanwang@gmail.com',
    description='Dice detection ROS2 node for the yutnori project.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dice_detector = dice_detector_pkg.detector_node:main',
        ],
    },
)

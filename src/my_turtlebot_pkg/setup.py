from setuptools import find_packages, setup

package_name = 'my_turtlebot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
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

        ],
    },
)

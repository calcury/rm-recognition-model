from setuptools import setup
import os
from glob import glob

package_name = 'robot_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='calcury',
    maintainer_email='calcury@AIM-RADAR',
    description='ROS2 robot detection node with YOLOv5',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_detector_node = robot_detector.robot_detector_node:main'
        ],
    },
)

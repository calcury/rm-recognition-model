from setuptools import setup
import os
from glob import glob

package_name = 'video_publisher'

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
    description='ROS2 video publisher node',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 核心修复：注册节点可执行文件
            'video_publisher_node = video_publisher.video_publisher_node:main'
        ],
    },
)

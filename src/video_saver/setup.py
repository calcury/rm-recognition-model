from setuptools import setup
import os
from glob import glob

package_name = 'video_saver'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 确保out目录能被创建
        (os.path.join('share', package_name, 'out'), []),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='calcury',
    maintainer_email='calcury@example.com',
    description='ROS2 video saver node',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'video_saver_node = video_saver.video_saver_node:main',
        ],
    },
)
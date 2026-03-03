from setuptools import setup, find_packages

package_name = 'video_processor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),  # 自动查找所有Python包
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 确保Python代码文件被安装到site-packages
        ('lib/python3.10/site-packages/' + package_name, 
            ['video_processor/video_processor_node.py', 'video_processor/__init__.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='calcury',
    maintainer_email='calcury@AIM-RADAR',
    description='ROS2 video processor node',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'video_processor_node = video_processor.video_processor_node:main'
        ],
    },
)

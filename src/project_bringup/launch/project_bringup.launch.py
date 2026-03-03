from launch import LaunchDescription
from launch.actions import ExecuteProcess
import os

def generate_launch_description():
    # 工作空间安装目录（绝对路径）
    install_dir = os.path.expanduser('~/aim-vision-2526-final-assessment/install')
    
    # 定义每个节点的执行命令（直接调用bin目录的可执行文件）
    nodes = [
        # 视频发布节点
        ExecuteProcess(
            cmd=[os.path.join(install_dir, 'video_publisher', 'bin', 'video_publisher_node')],
            output='screen',
            name='video_publisher'
        ),
        # 视频处理节点
        ExecuteProcess(
            cmd=[os.path.join(install_dir, 'video_processor', 'bin', 'video_processor_node')],
            output='screen',
            name='video_processor'
        ),
        # 机器人检测节点
        ExecuteProcess(
            cmd=[os.path.join(install_dir, 'robot_detector', 'bin', 'robot_detector_node')],
            output='screen',
            name='robot_detector'
        ),
        # 视频保存节点
        ExecuteProcess(
            cmd=[os.path.join(install_dir, 'video_saver', 'bin', 'video_saver_node')],
            output='screen',
            name='video_saver'
        )
    ]
    
    return LaunchDescription(nodes)

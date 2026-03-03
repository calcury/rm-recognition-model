import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        
        # 初始化发布者
        self.publisher_ = self.create_publisher(Image, '/input_video', 10)
        
        # 初始化CVBridge（转换OpenCV图像到ROS2 Image消息）
        self.bridge = CvBridge()
        
        # 视频文件路径（注意：建议根据实际路径调整，比如加上用户名）
        self.video_path = '/home/materials/input.mp4'
        if not os.path.exists(self.video_path):
            self.get_logger().fatal(f"视频文件不存在: {self.video_path}")
            rclpy.shutdown()
            return
        
        # 打开视频文件
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.get_logger().fatal("无法打开视频文件")
            rclpy.shutdown()
            return
        
        # 获取视频关键参数
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 视频帧率
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
        self.total_seconds = self.total_frames / self.fps  # 视频总时长（秒）
        
        # 打印视频基础信息
        self.get_logger().info(f"视频信息 - 总帧数: {self.total_frames}, 帧率: {self.fps} FPS, 总时长: {self.total_seconds:.2f} 秒")
        
        # 根据帧率设置定时器
        timer_period = 1.0 / self.fps  # 发布周期（秒）
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # 读取一帧视频
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().info("== 视频播放完毕 ==")
            self.timer.cancel()
            self.cap.release()
            self.destroy_node()
            rclpy.shutdown()
            return
        
        # 获取当前播放帧数
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        # 计算已播放时间和剩余时间
        elapsed_seconds = current_frame / self.fps
        remaining_seconds = self.total_seconds - elapsed_seconds
        
        # 输出播放进度日志
        if current_frame % 10 == 0:
            self.get_logger().info(
                f"播放进度 - 当前帧: {current_frame}/{self.total_frames}, "
            )

        # if current_frame == 200:
        #     self.get_logger().info("== 视频播放完毕 ==")
        #     self.timer.cancel()
        #     self.cap.release()
        #     self.destroy_node()
        #     rclpy.shutdown()
        #     return
        
        # 转换为ROS2 Image消息并发布
        try:
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(img_msg)
        except Exception as e:
            self.get_logger().error(f"图像转换失败: {str(e)}")

    def destroy_node(self):
        # 释放资源
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = VideoPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("用户中断，停止播放")
    finally:
        # 确保资源都被正确释放
        if node:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
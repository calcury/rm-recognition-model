import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import sys
import time

class VideoSaver(Node):
    def __init__(self):
        super().__init__('video_saver')
        
        # 1. 修复：输出目录改为任务要求的 out/ （工作空间根目录下）
        self.out_dir = os.path.join(os.path.expanduser("~"), "aim-vision-2526-final-assessment", "out")
        # 兜底：如果上述路径失败，使用当前目录
        try:
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir, mode=0o755, exist_ok=True)
                self.get_logger().info(f"✅ 创建输出目录: {self.out_dir}")
            else:
                self.get_logger().info(f"✅ 输出目录已存在: {self.out_dir}")
        except Exception as e:
            self.out_dir = os.path.join(os.getcwd(), "out")
            os.makedirs(self.out_dir, exist_ok=True)
            self.get_logger().warn(f"⚠️  原目录创建失败，使用兜底目录: {self.out_dir}, 错误: {str(e)}")
        
        # 初始化CVBridge
        self.bridge = CvBridge()
        
        # 视频写入器
        self.edge_writer = None
        self.detect_writer = None
        
        # 2. 修复：默认帧率改为更通用的30，可根据实际输入调整
        self.fps = 60  
        self.edge_size = None
        self.detect_size = None  # 分开存储尺寸，避免两个视频尺寸不一致导致错误
        
        # 新增：帧计数，监控接收到/写入的帧数
        self.edge_frame_count = 0
        self.detect_frame_count = 0
        
        # 订阅话题
        self.edge_sub = self.create_subscription(
            Image,
            '/output_edge_video',
            self.edge_callback,
            10)
        self.detect_sub = self.create_subscription(
            Image,
            '/output_detect_video',
            self.detect_callback,
            10)
        
        # 3. 增加：注册退出回调，确保资源释放
        self.create_timer(1.0, self.timer_callback)  # 心跳定时器，打印帧计数
        self.get_logger().info("✅ video_saver节点初始化完成")

    def init_writer(self, frame, writer_type):
        """初始化视频写入器（分开处理两个视频的尺寸）"""
        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 兼容大部分播放器
        file_path = ""
        
        if writer_type == 'edge':
            self.edge_size = (width, height)
            file_path = os.path.join(self.out_dir, 'output_edge_video.mp4')
            self.edge_writer = cv2.VideoWriter(file_path, fourcc, self.fps, self.edge_size)
            self.get_logger().info(f"✅ 边缘检测视频写入器初始化完成，保存路径: {file_path} | 帧率: {self.fps} | 尺寸: {self.edge_size}")
        elif writer_type == 'detect':
            self.detect_size = (width, height)
            file_path = os.path.join(self.out_dir, 'output_detect_video.mp4')
            self.detect_writer = cv2.VideoWriter(file_path, fourcc, self.fps, self.detect_size)
            self.get_logger().info(f"✅ 检测视频写入器初始化完成，保存路径: {file_path} | 帧率: {self.fps} | 尺寸: {self.detect_size}")
        
        # 验证写入器是否成功创建
        if (writer_type == 'edge' and not self.edge_writer.isOpened()) or \
           (writer_type == 'detect' and not self.detect_writer.isOpened()):
            self.get_logger().error(f"❌ 视频写入器创建失败，请检查路径权限: {file_path}")

    def edge_callback(self, msg):
        try:
            # 修复：指定encoding为bgr8，确保格式正确
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.edge_frame_count += 1
            
            if self.edge_writer is None:
                self.init_writer(frame, 'edge')
            
            # 写入前验证帧尺寸匹配
            if frame.shape[1] == self.edge_size[0] and frame.shape[0] == self.edge_size[1]:
                self.edge_writer.write(frame)
                # 每20帧打印一次计数，监控进度
                if self.edge_frame_count % 20 == 0:
                    self.get_logger().info(f"边缘视频已写入 {self.edge_frame_count} 帧")
            else:
                self.get_logger().warn(f"边缘视频帧尺寸不匹配，期望: {self.edge_size}, 实际: {(frame.shape[1], frame.shape[0])}")
        except Exception as e:
            self.get_logger().error(f"保存边缘视频失败: {str(e)}")

    def detect_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.detect_frame_count += 1
            
            if self.detect_writer is None:
                self.init_writer(frame, 'detect')
            
            # 写入前验证帧尺寸匹配
            if frame.shape[1] == self.detect_size[0] and frame.shape[0] == self.detect_size[1]:
                self.detect_writer.write(frame)
                # 每20帧打印一次计数，监控进度
                if self.detect_frame_count % 20 == 0:
                    self.get_logger().info(f"检测视频已写入 {self.detect_frame_count} 帧")
            else:
                self.get_logger().warn(f"检测视频帧尺寸不匹配，期望: {self.detect_size}, 实际: {(frame.shape[1], frame.shape[0])}")
        except Exception as e:
            self.get_logger().error(f"保存检测视频失败: {str(e)}")

    def timer_callback(self):
        """心跳定时器，打印帧计数，监控节点状态"""
        pass

    def safe_release(self):
        """安全释放视频写入器（核心修复：强制刷缓存+验证释放）"""
        try:
            # 1. 边缘视频写入器释放
            if self.edge_writer is not None and self.edge_writer.isOpened():
                # 强制刷写缓存（关键！避免最后几帧丢失）
                cv2.waitKey(1)
                self.edge_writer.release()
                self.get_logger().info(f"边缘视频写入器已释放 | 总计写入 {self.edge_frame_count} 帧")
            # 2. 检测视频写入器释放
            if self.detect_writer is not None and self.detect_writer.isOpened():
                cv2.waitKey(1)
                self.detect_writer.release()
                self.get_logger().info(f"检测视频写入器已释放 | 总计写入 {self.detect_frame_count} 帧")
        except Exception as e:
            self.get_logger().error(f"释放资源时出错: {str(e)}")

    def destroy_node(self):
        self.safe_release()
        self.get_logger().info(f"video_saver节点已退出 | 最终计数 - 边缘视频: {self.edge_frame_count} 帧 | 检测视频: {self.detect_frame_count} 帧")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = VideoSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # 修复：用node.get_logger()而非self
        node.get_logger().info("接收到退出信号，正在保存视频...")
    except Exception as e:
        node.get_logger().fatal(f"节点运行出错: {str(e)}")
    finally:
        # 强制释放资源，确保视频文件完整
        node.safe_release()
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()
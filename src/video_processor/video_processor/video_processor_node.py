import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class VideoProcessor(Node):
    def __init__(self):
        super().__init__('video_processor')
        self.subscription = self.create_subscription(
            Image, '/input_video', self.listener_callback, 10)
        self.publisher_ = self.create_publisher(Image, '/output_edge_video', 10)
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            processed_msg = self.bridge.cv2_to_imgmsg(edges_bgr, encoding="bgr8")
            self.publisher_.publish(processed_msg)
        except Exception as e:
            self.get_logger().error(f"图像处理失败: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = VideoProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

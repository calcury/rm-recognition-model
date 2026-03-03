import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import os
import onnxruntime as ort

class RobotDetector(Node):
    def __init__(self):
        super().__init__('robot_detector')
        # 订阅发布话题
        self.subscription = self.create_subscription(
            Image, '/input_video', self.callback, 10)
        self.pub = self.create_publisher(Image, '/output_detect_video', 10)
        self.bridge = CvBridge()

        # 模型路径
        self.onnx_path = "/home/calcury/aim-vision-2526-final-assessment/src/robot_detector/resource/best.onnx"
        self.class_path = "/home/calcury/aim-vision-2526-final-assessment/src/robot_detector/resource/robot.names"

        # 校验文件
        self._check_file_exists()

        # 加载ONNX模型
        self.session = ort.InferenceSession(self.onnx_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.input_size = (416, 416) 

        # 加载类别和参数
        with open(self.class_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines() if line.strip()]
        if not self.classes:
            self.classes = ["rm"]
            with open(self.class_path, 'w') as f:
                f.write("rm")
        self.get_logger().info(f"加载类别列表：{self.classes} | 类别数量：{len(self.classes)}")
        
        self.conf_threshold = 0.15
        self.nms_threshold = 0.5
        # YOLOv8n 416×416 原始锚框
        self.anchors = np.array([[10,13, 16,30, 33,23],
                                 [30,61, 62,45, 59,119],
                                 [116,90, 156,198, 373,326]]) / 8
        self.strides = np.array([8, 16, 32])

        # 帧计数
        self.frame_count = 0

    def _check_file_exists(self):
        """校验文件"""
        missing_files = []
        for file_path in [self.onnx_path, self.class_path]:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        if missing_files:
            self.get_logger().fatal(f"文件缺失：{', '.join(missing_files)}")
            if self.class_path in missing_files:
                with open(self.class_path, 'w') as f:
                    f.write("rm")
                self.get_logger().info(f"💡 已创建类别文件：{self.class_path}")
            raise FileNotFoundError(f"文件缺失：{', '.join(missing_files)}")

    def _preprocess(self, frame):
        """纯拉伸预处理（和模型导出时一致）"""
        # 直接拉伸到416×416
        img = cv2.resize(frame, self.input_size, interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.expand_dims(img, axis=0)
        return img

    def _decode_yolov8_raw(self, pred, frame_w, frame_h):
        """解码YOLOv8原始检测头输出（适配(1,5,3549)维度）"""
        boxes = []
        confidences = []
        pred = pred[0].T
        
        # 遍历所有锚框
        for i in range(len(pred)):
            x, y, w, h, conf = pred[i]
            if conf < self.conf_threshold:
                continue
            
            # 解码YOLOv8原始坐标（中心xy+宽高 → 左上角xy+宽高）
            x1 = (x - w/2) * frame_w / self.input_size[0]
            y1 = (y - h/2) * frame_h / self.input_size[1]
            x2 = (x + w/2) * frame_w / self.input_size[0]
            y2 = (y + h/2) * frame_h / self.input_size[1]
            
            # 转换为OpenCV NMS格式 [x1, y1, w, h]
            w_box = x2 - x1
            h_box = y2 - y1
            
            # 边界检查
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            w_box = max(1, int(w_box))
            h_box = max(1, int(h_box))
            
            boxes.append([x1, y1, w_box, h_box])
            confidences.append(float(conf))
        
        return boxes, confidences

    def _draw_boxes(self, frame, indices, boxes, confidences):
        """绘制绿框（简化版，只画有效框）"""
        drawn_count = 0
        if indices is None or len(indices) == 0:
            return drawn_count
        
        # 统一indices格式
        if isinstance(indices, np.ndarray):
            indices = indices.flatten().tolist()
        elif not isinstance(indices, list):
            indices = [int(indices)]
        
        # 绘制绿框
        for i in indices:
            try:
                idx = int(i)
                if idx < 0 or idx >= len(boxes):
                    continue
                x, y, w, h = boxes[idx]
                conf = confidences[idx] if idx < len(confidences) else 0.0
                
                # 绘制绿框
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                # 绘制标签
                label = f"rm: {conf:.2f}"
                label_y = y - 10 if y - 10 > 10 else y + 20
                cv2.putText(frame, label, (x, label_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                drawn_count += 1
            except Exception as e:
                self.get_logger().warn(f"绘制框出错：{str(e)}")
                continue
        return drawn_count

    def callback(self, msg):
        """核心回调（适配(1,5,3549)维度）"""
        frame = None
        try:
            # ROS2 → OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            frame_h, frame_w = frame.shape[:2]

            # 预处理（直接拉伸，和模型一致）
            blob = self._preprocess(frame)
            
            # 模型推理
            pred = self.session.run([self.output_name], {self.input_name: blob})[0]

            # 解码原始检测输出
            boxes, confidences = self._decode_yolov8_raw(pred, frame_w, frame_h)
            drawn_count = 0
            
            # NMS去重 + 绘制
            if len(boxes) > 0:
                indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
                drawn_count = self._draw_boxes(frame, indices, boxes, confidences)
            
            # 日志
            # self.get_logger().info(f"绘制绿框：{drawn_count}个")
            self.frame_count += 1

        except Exception as e:
            self.get_logger().error(f"回调出错：{str(e)}，继续运行")
            if frame is None:
                frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        
        # 发布画框后的帧
        try:
            self.pub.publish(self.bridge.cv2_to_imgmsg(frame, 'bgr8'))
        except Exception as e:
            self.get_logger().error(f"发布帧失败：{str(e)}")

def main(args=None):
    rclpy.init(args=args)
    try:
        node = RobotDetector()
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f"手动停止，共处理 {node.frame_count} 帧")
    except Exception as e:
        print(f"节点启动失败：{str(e)}")
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
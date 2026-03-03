import cv2
import numpy as np
import onnxruntime as ort

# ===================== 配置项（你需要修改的部分） =====================
TEST_IMAGE_PATH = "test_robot.png"  # 你的测试图片路径
ONNX_MODEL_PATH = "best.onnx"       # 你的ONNX模型路径
# 人工标注的目标框（格式：[x1, y1, x2, y2]，从截图红框中提取）
# 示例：ANNOTATED_BOX = [100, 80, 300, 250]
ANNOTATED_BOX = [0, 0, 0, 0]  # 替换成你红框的实际坐标！
CONF_THRESHOLD = 0.1
# =====================================================================

def calculate_iou(box1, box2):
    """计算两个框的IOU（交并比），判断匹配度"""
    # box格式：[x1, y1, x2, y2]
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    # 计算交集面积
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    # 计算并集面积
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    
    # 计算IOU
    iou = inter_area / union_area if union_area > 0 else 0.0
    return iou

def preprocess_image(image, input_size=(416, 416)):
    """预处理：直接拉伸（匹配你的模型）"""
    img = cv2.resize(image, input_size, interpolation=cv2.INTER_LINEAR)
    img = img.astype(np.float32) / 255.0
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0)
    return img

def decode_detections(pred, frame_w, frame_h, input_size=(416, 416)):
    """解码模型输出（适配(1,5,3549)维度）"""
    detections = []
    pred = pred[0].T  # (3549,5)
    
    for i in range(len(pred)):
        x, y, w, h, conf = pred[i]
        if conf < CONF_THRESHOLD:
            continue
        
        # 解码坐标：中心xy+宽高 → 左上角xy+右下角xy
        x1 = (x - w/2) * frame_w / input_size[0]
        y1 = (y - h/2) * frame_h / input_size[1]
        x2 = (x + w/2) * frame_w / input_size[0]
        y2 = (y + h/2) * frame_h / input_size[1]
        
        # 边界检查
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(frame_w-1, int(x2))
        y2 = min(frame_h-1, int(y2))
        
        detections.append({
            "box": [x1, y1, x2, y2],
            "conf": conf,
            "iou": calculate_iou(ANNOTATED_BOX, [x1, y1, x2, y2])
        })
    
    # 按IOU排序，取匹配度最高的框
    if detections:
        detections = sorted(detections, key=lambda x: x["iou"], reverse=True)
    return detections

def main():
    # 1. 加载图片
    img = cv2.imread(TEST_IMAGE_PATH)
    if img is None:
        print(f"❌ 无法加载图片：{TEST_IMAGE_PATH}")
        return
    frame_h, frame_w = img.shape[:2]
    print(f"✅ 加载图片成功，尺寸：{frame_w}×{frame_h}")
    
    # 2. 画出人工标注的红框
    if ANNOTATED_BOX != [0,0,0,0]:
        x1, y1, x2, y2 = ANNOTATED_BOX
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)  # 红框（粗4像素）
        cv2.putText(img, "Annotated", (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print(f"✅ 已绘制人工标注红框：{ANNOTATED_BOX}")
    else:
        print("⚠️  请先填写ANNOTATED_BOX的实际坐标！")
    
    # 3. 加载模型并推理
    try:
        session = ort.InferenceSession(ONNX_MODEL_PATH, providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        print(f"✅ 加载模型成功，输出维度：{session.get_outputs()[0].shape}")
        
        # 预处理+推理
        blob = preprocess_image(img)
        pred = session.run([output_name], {input_name: blob})[0]
        
        # 解码检测结果
        detections = decode_detections(pred, frame_w, frame_h)
        print(f"✅ 解码出 {len(detections)} 个有效检测框")
        
        # 4. 画出模型检测的绿框（取IOU最高的）
        if detections:
            best_det = detections[0]
            box = best_det["box"]
            conf = best_det["conf"]
            iou = best_det["iou"]
            
            x1, y1, x2, y2 = box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)  # 绿框（粗3像素）
            cv2.putText(img, f"Detected (IOU:{iou:.2f}, Conf:{conf:.2f})", (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 打印关键指标
            print(f"\n===== 标注验证结果 =====")
            print(f"模型检测最佳框：{box}")
            print(f"置信度：{conf:.4f}")
            print(f"与标注框IOU：{iou:.4f}")
            if iou >= 0.5:
                print(f"✅ 标注正确（IOU≥0.5）")
            else:
                print(f"❌ 标注/检测偏移（IOU<0.5）")
        else:
            print("❌ 模型未检测到有效目标")
    
    except Exception as e:
        print(f"❌ 模型推理失败：{str(e)}")
    
    # 5. 保存对比图
    save_path = "annotation_verify_result.jpg"
    cv2.imwrite(save_path, img)
    print(f"\n✅ 对比图已保存到：{save_path}")

if __name__ == "__main__":
    main()

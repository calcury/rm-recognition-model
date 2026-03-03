from ultralytics import YOLO
import warnings
warnings.filterwarnings("ignore")

# 加载训练好的best.pt（注意：替换为实际路径）
model = YOLO("runs/detect/robot_train/robot_model/weights/best.pt")

# 适配旧版本的导出参数（移除不支持的img_format/normalize）
model.export(
    format="onnx",
    imgsz=416,        # 和训练/推理严格一致
    opset=11,         # 兼容旧版本ONNX Runtime
    dynamic=False,    # 关闭动态维度（关键！保证维度固定）
    simplify=True,    # 简化模型结构
    batch=1,          # 固定batch=1
    device="cpu"
)
print("✅ YOLOv8 ONNX模型导出成功（旧版本适配版）：best.onnx")

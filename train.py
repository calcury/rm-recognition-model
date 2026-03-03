from ultralytics import YOLO
import warnings
warnings.filterwarnings("ignore")

# 1. 加载超轻量化预训练模型（YOLOv8n）
model = YOLO('yolov8n.pt')

# 2. 训练配置（核心：和推理维度严格对齐）
results = model.train(
    data='dataset/data.yaml',  # 数据集配置文件路径
    epochs=50,                       # 训练轮数（小数据集50足够）
    batch=8,                         # 批次大小（服务器内存小则设为4）
    imgsz=416,                       # 固定416×416（和推理一致）
    device='cpu',                    # 纯CPU训练（无GPU也可）
    patience=10,                     # 早停（避免过拟合）
    lr0=0.001,                       # 初始学习率（小值适配小数据集）
    weight_decay=0.0005,             # 权重衰减（防止过拟合）
    save=True,                       # 保存最佳模型
    project='robot_train',           # 训练结果保存目录
    name='robot_model',              # 模型名称
    exist_ok=True,                   # 覆盖已有目录
    rect=False,                      # 关闭矩形训练（保证输入尺寸固定）
    mosaic=0.0                       # 关闭mosaic增强（小数据集更稳定）
)

# 3. 验证模型
metrics = model.val()
print(f"✅ 模型验证完成，mAP@0.5：{metrics.box.map50:.2f}")

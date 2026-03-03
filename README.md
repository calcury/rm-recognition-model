# AIM-Vision 2526 Final Assessment
实现视频的边缘检测、目标检测及视频处理

## AI 使用声明
- 期间很多问题都是通过AI解决的，但是在AI生成代码之后，我都会重新过一遍代码确保理解具体实现过程，并基于这个结果做一些升级改进

## 一、环境配置
### 1. 加载 ROS2 环境
```bash
# 将 ros2 添加到环境变量 (每次使用ros2指令前运行)
source /opt/ros/humble/setup.bash
```

### 2. 模型配置
尝试使用了 `YOLOv5` 开源模型，但是 `YOLOv5` 在github上的开源模型对应的 `.onnx` 最新版本和当前环境的 openCV 不兼容，旧的版本无法找到(resource not found)

最后决定换了一个更轻量的模型 `YOLOv4-tiny` ，模型不包含机器人类，但是稍加调整也可以用作机器人目标检测（准确率不高），后续要优化可以考虑升级模型（升级opencv/pytorch开发环境）

测试后发现机器人和该模型里 `{"car", "truck", "person"}` 三个类别相似程度最高，就借此进行识别(反而和该模型里robot类相似度不高)
```bash
# 模型通用配置文件
https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
# 模型权重参数
https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights
# 类标签
https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names
```
期间总共测试了6个预训练机器人识别模型，但是准确率都不是很理想，于是基于 `yolov8n` 重新训练了一个超轻量模型，包括采集数据(网上找比赛截图), 格式化, 打标签, 训练, 测试，然后重新部署，再调整阈值来提高识别准确率



## 二、视频调试脚本
### 1. 查看视频信息
```bash
# 进入目录+快速运行
cd ~/aim-vision-2526-final-assessment
python3 scripts/video_info.py
```

### 2. 生成灰度视频
```bash
# 进入目录+快速运行
cd ~/aim-vision-2526-final-assessment/scripts
# 由于 build 文件夹被 gitignore 了，复现演示需要重新创建目录
mkdir -p build
cd build
cmake .. 
make
# 输出路径 out/output_grayscale.mp4
./video_to_grayscale  
```

## 三、边缘检测、目标检测及视频处理
### 1. Colcon Build
```bash
# 进入目录+快速编译
cd ~/aim-vision-2526-final-assessment
colcon build
source install/setup.bash
```

### 2. 一次拉起
```bash
# 将 ros2 添加到环境变量
source /opt/ros/humble/setup.bash
source install/setup.bash
cd ~/aim-vision-2526-final-assessment
ros2 launch project_bringup project_bringup.launch.py
```

## 四、运行结果
尝试使用了 `Xming` 转发，但是由于网络问题，实际效率极低而且卡顿严重，最后使用 `scp` 将视频下载到自己的电脑上分析，中间先用自己的虚拟机调试完成后再同步到雷达主机

```bash
# ForwardX11转发
ssh -Y calcury@dev.uonaim.tech -p 51222
source /opt/ros/noetic/setup.bash
```
```bash
# 通过 scp 下载结果
scp -P 51222 calcury@dev.uonaim.tech:/home/calcury/aim-vision-2526-final-assessment/out/output_grayscale.mp4 ./ # 灰度转化
scp -P 51222 calcury@dev.uonaim.tech:/home/calcury/aim-vision-2526-final-assessment/out/output_edge_video.mp4 ./ # 边缘检测
scp -P 51222 calcury@dev.uonaim.tech:/home/calcury/aim-vision-2526-final-assessment/out/output_detect_video.mp4 ./ #目标检测
```
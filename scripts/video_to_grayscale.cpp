#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>

// 固定路径配置
const std::string INPUT_VIDEO_PATH = "/home/materials/input.mp4";
// 项目根目录
const std::string PROJECT_ROOT = "/home/calcury/aim-vision-2526-final-assessment";
const std::string OUTPUT_ABS_PATH = PROJECT_ROOT + "/out/output_grayscale.mp4";

int main() {
    // 打开输入视频
    cv::VideoCapture cap(INPUT_VIDEO_PATH);

    // 获取视频基础参数
    int fps = static_cast<int>(cap.get(cv::CAP_PROP_FPS));
    int width = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_WIDTH));
    int height = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_HEIGHT));
    int total_frames = static_cast<int>(cap.get(cv::CAP_PROP_FRAME_COUNT));

    if (fps <= 0) fps = 30;

    // 配置视频写入器
    int fourcc = cv::VideoWriter::fourcc('m', 'p', '4', 'v');
    // 灰度视频为单通道，最后一个参数设为false
    cv::VideoWriter writer(OUTPUT_ABS_PATH, fourcc, fps, cv::Size(width, height), false);

    // 逐帧读取、转灰度、写入
    cv::Mat frame, gray_frame;
    int frame_count = 0;
    while (cap.read(frame)) {
        // 彩色转灰度：BGR -> GRAY
        cv::cvtColor(frame, gray_frame, cv::COLOR_BGR2GRAY);
        // 写入灰度帧
        writer.write(gray_frame);

        frame_count++;
    }

    // 释放资源
    cap.release();
    writer.release();
    std::cout << "===== 转换完成 =====" << std::endl;
    return 0;
}
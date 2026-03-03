import cv2
import sys
from pathlib import Path

# 固定视频绝对路径（核心修改点）
VIDEO_PATH = "/home/materials/input.mp4"


def get_video_info(video_path: str) -> dict:
    """
    读取视频文件的基础元信息
    :param video_path: 视频文件路径
    :return: 包含视频信息的字典，读取失败返回None
    """
    # 打开视频流
    cap = cv2.VideoCapture(video_path)

    try:
        # 获取视频基本信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))               
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration_sec = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps if fps > 0 else 0.0

        # 视频编码格式
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        # 封装信息字典
        info = {
            "分辨率": f"{width}*{height}",
            "帧率": round(fps, 2),
            "总时长(s)": round(duration_sec, 2),
            "编码格式": codec,
        }
        return info

    finally:
        # 释放视频资源
        cap.release()


def print_video_info(info: dict):
    """格式化打印视频信息到终端"""
    if not info:
        return

    print("=" * 50)
    print("视频基础信息")
    print("=" * 50)
    for key, value in info.items():
        print(f"{key}: {value}")
    print("=" * 50)

if __name__ == "__main__":
    video_info = get_video_info(VIDEO_PATH)
    print_video_info(video_info)
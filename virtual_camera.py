#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 虚拟摄像头程序
模拟摄像头设备，循环播放指定视频
"""

import cv2
import pyvirtualcam
import numpy as np
import time
import sys
from pathlib import Path


class VirtualCamera:
    def __init__(self, video_path, fps=30, width=1280, height=720):
        """
        初始化虚拟摄像头
        
        Args:
            video_path: 要播放的视频文件路径
            fps: 帧率
            width: 输出宽度
            height: 输出高度
        """
        self.video_path = video_path
        self.fps = fps
        self.width = width
        self.height = height
        self.cap = None
        
    def load_video(self):
        """加载视频文件"""
        if not Path(self.video_path).exists():
            raise FileNotFoundError(f"视频文件不存在: {self.video_path}")
        
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        # 获取视频信息
        video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息:")
        print(f"  文件: {self.video_path}")
        print(f"  分辨率: {video_width}x{video_height}")
        print(f"  帧率: {video_fps} FPS")
        print(f"  总帧数: {frame_count}")
        print(f"\n输出设置:")
        print(f"  分辨率: {self.width}x{self.height}")
        print(f"  帧率: {self.fps} FPS")
        
    def run(self):
        """运行虚拟摄像头"""
        self.load_video()
        
        # 创建虚拟摄像头
        with pyvirtualcam.Camera(width=self.width, height=self.height, 
                                 fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            print(f'\n虚拟摄像头已启动: {cam.device}')
            print(f'摄像头名称: Virtual Camera')
            print('按 Ctrl+C 停止\n')
            
            frame_time = 1.0 / self.fps
            frame_count = 0
            
            try:
                while True:
                    start_time = time.time()
                    
                    # 读取视频帧
                    ret, frame = self.cap.read()
                    
                    # 如果视频播放完毕，重新开始
                    if not ret:
                        print("视频播放完毕，重新开始...")
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                        
                        if not ret:
                            print("错误：无法读取视频帧")
                            break
                    
                    # 调整帧大小
                    if frame.shape[1] != self.width or frame.shape[0] != self.height:
                        frame = cv2.resize(frame, (self.width, self.height))
                    
                    # 发送到虚拟摄像头
                    cam.send(frame)
                    
                    frame_count += 1
                    if frame_count % 100 == 0:
                        print(f"已播放 {frame_count} 帧")
                    
                    # 控制帧率
                    elapsed = time.time() - start_time
                    sleep_time = frame_time - elapsed
                    if sleep_time > 0:
                        cam.sleep_until_next_frame()
                    
            except KeyboardInterrupt:
                print("\n正在停止虚拟摄像头...")
            finally:
                self.cap.release()
                print("虚拟摄像头已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Windows 虚拟摄像头 - 播放视频文件')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--fps', type=int, default=30, help='输出帧率 (默认: 30)')
    parser.add_argument('--width', type=int, default=1280, help='输出宽度 (默认: 1280)')
    parser.add_argument('--height', type=int, default=720, help='输出高度 (默认: 720)')
    
    args = parser.parse_args()
    
    try:
        cam = VirtualCamera(args.video, fps=args.fps, width=args.width, height=args.height)
        cam.run()
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


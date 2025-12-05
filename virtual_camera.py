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
    def __init__(self, video_path, fps=30, width=1280, height=720, wait_mode=True):
        """
        初始化虚拟摄像头
        
        Args:
            video_path: 要播放的视频文件路径
            fps: 帧率
            width: 输出宽度
            height: 输出高度
            wait_mode: 是否等待模式（启动后显示待机画面）
        """
        self.video_path = video_path
        self.fps = fps
        self.width = width
        self.height = height
        self.cap = None
        self.wait_mode = wait_mode
        self.playing = False
        
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
        
    def create_standby_frame(self):
        """创建待机画面"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # 设置深色背景
        frame[:, :] = (30, 30, 30)
        
        # 添加文字
        texts = [
            ("虚拟摄像头已就绪", (255, 255, 255), 2.0, -120),
            ("等待开始播放...", (200, 200, 200), 1.2, -40),
        ]
        
        for text, color, scale, y_offset in texts:
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = int(scale * 2)
            
            # 获取文字大小
            (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)
            
            # 计算居中位置
            x = (self.width - text_width) // 2
            y = (self.height // 2) + y_offset
            
            # 添加阴影
            cv2.putText(frame, text, (x + 3, y + 3), font, scale, (0, 0, 0), thickness)
            # 添加主文字
            cv2.putText(frame, text, (x, y), font, scale, color, thickness)
        
        # 添加提示信息
        hint_text = "按 Enter 开始播放 | Ctrl+C 退出"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.7
        thickness = 1
        (text_width, text_height), _ = cv2.getTextSize(hint_text, font, scale, thickness)
        x = (self.width - text_width) // 2
        y = self.height - 50
        cv2.putText(frame, hint_text, (x, y), font, scale, (150, 150, 150), thickness)
        
        return frame
    
    def check_for_start_signal(self):
        """非阻塞地检查是否有开始信号"""
        import select
        import sys
        
        # Windows系统不支持select，改用其他方式
        if sys.platform == 'win32':
            import msvcrt
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in [b'\r', b'\n']:  # Enter键
                    return True
        else:
            # Unix系统使用select
            if select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                return True
        return False
    
    def run(self):
        """运行虚拟摄像头"""
        self.load_video()
        
        # 创建虚拟摄像头
        with pyvirtualcam.Camera(width=self.width, height=self.height, 
                                 fps=self.fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            print(f'\n虚拟摄像头已启动: {cam.device}')
            print(f'摄像头名称: Virtual Camera')
            
            if self.wait_mode:
                print('\n=== 待机模式 ===')
                print('虚拟摄像头已就绪，显示待机画面')
                print('按 Enter 键开始播放视频')
                print('按 Ctrl+C 停止\n')
            else:
                print('按 Ctrl+C 停止\n')
            
            frame_time = 1.0 / self.fps
            frame_count = 0
            standby_frame = self.create_standby_frame()
            
            try:
                while True:
                    start_time = time.time()
                    
                    # 如果是等待模式且还未开始播放
                    if self.wait_mode and not self.playing:
                        # 检查是否有开始信号
                        if self.check_for_start_signal():
                            self.playing = True
                            print("\n=== 开始播放视频 ===\n")
                        else:
                            # 发送待机画面
                            cam.send(standby_frame)
                            cam.sleep_until_next_frame()
                            continue
                    
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
    parser.add_argument('--no-wait', action='store_true', 
                       help='禁用等待模式，立即播放视频')
    
    args = parser.parse_args()
    
    try:
        cam = VirtualCamera(args.video, fps=args.fps, width=args.width, 
                          height=args.height, wait_mode=not args.no_wait)
        cam.run()
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


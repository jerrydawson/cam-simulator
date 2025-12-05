#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试视频
如果你没有视频文件，可以用这个脚本生成一个测试视频
"""

import cv2
import numpy as np
from datetime import datetime


def create_test_video(output_path='test_video.mp4', duration=10, fps=30, 
                     width=1280, height=720):
    """
    创建一个测试视频
    
    Args:
        output_path: 输出文件路径
        duration: 视频时长（秒）
        fps: 帧率
        width: 宽度
        height: 高度
    """
    print(f"正在创建测试视频...")
    print(f"  输出文件: {output_path}")
    print(f"  时长: {duration} 秒")
    print(f"  分辨率: {width}x{height}")
    print(f"  帧率: {fps} FPS")
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    for frame_num in range(total_frames):
        # 创建彩色背景（渐变色）
        hue = int((frame_num / total_frames) * 180)
        hsv = np.zeros((height, width, 3), dtype=np.uint8)
        hsv[:, :, 0] = hue
        hsv[:, :, 1] = 255
        hsv[:, :, 2] = 255
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # 添加文字信息
        text_lines = [
            "虚拟摄像头测试视频",
            f"帧: {frame_num + 1}/{total_frames}",
            f"时间: {frame_num / fps:.2f}s / {duration}s",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        y_offset = 100
        for i, text in enumerate(text_lines):
            y = y_offset + i * 60
            
            # 添加阴影效果
            cv2.putText(frame, text, (52, y + 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
            
            # 添加主文字
            cv2.putText(frame, text, (50, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # 添加移动的圆形
        circle_x = int((frame_num / total_frames) * width)
        circle_y = height // 2
        cv2.circle(frame, (circle_x, circle_y), 30, (0, 255, 0), -1)
        cv2.circle(frame, (circle_x, circle_y), 35, (255, 255, 255), 2)
        
        # 添加进度条
        bar_width = int((frame_num / total_frames) * (width - 100))
        cv2.rectangle(frame, (50, height - 50), (50 + bar_width, height - 30), 
                     (0, 255, 0), -1)
        cv2.rectangle(frame, (50, height - 50), (width - 50, height - 30), 
                     (255, 255, 255), 2)
        
        out.write(frame)
        
        # 显示进度
        if (frame_num + 1) % fps == 0:
            print(f"  进度: {frame_num + 1}/{total_frames} 帧 "
                  f"({(frame_num + 1) / total_frames * 100:.1f}%)")
    
    out.release()
    print(f"\n测试视频创建完成: {output_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='创建测试视频')
    parser.add_argument('--output', default='test_video.mp4', 
                       help='输出文件路径 (默认: test_video.mp4)')
    parser.add_argument('--duration', type=int, default=10, 
                       help='视频时长（秒）(默认: 10)')
    parser.add_argument('--fps', type=int, default=30, 
                       help='帧率 (默认: 30)')
    parser.add_argument('--width', type=int, default=1280, 
                       help='宽度 (默认: 1280)')
    parser.add_argument('--height', type=int, default=720, 
                       help='高度 (默认: 720)')
    
    args = parser.parse_args()
    
    print("========================================")
    print("测试视频生成器")
    print("========================================\n")
    
    create_test_video(
        output_path=args.output,
        duration=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height
    )
    
    print("\n使用方法:")
    print(f"  python virtual_camera.py {args.output}")
    print(f"  python virtual_camera_gui.py")


if __name__ == '__main__':
    main()


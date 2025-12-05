#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试虚拟摄像头是否正常工作
打开摄像头预览窗口
"""

import cv2
import sys


def list_cameras():
    """列出所有可用的摄像头"""
    print("正在扫描摄像头设备...\n")
    
    available_cameras = []
    
    for i in range(10):  # 检查前10个设备
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps
                })
                
                print(f"摄像头 {i}:")
                print(f"  分辨率: {width}x{height}")
                print(f"  帧率: {fps} FPS")
                print()
            
            cap.release()
    
    return available_cameras


def test_camera(camera_index):
    """测试指定摄像头"""
    print(f"正在打开摄像头 {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"错误：无法打开摄像头 {camera_index}")
        return
    
    print("摄像头已打开")
    print("按 'q' 或 ESC 退出预览\n")
    
    cv2.namedWindow('Camera Test', cv2.WINDOW_NORMAL)
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("警告：无法读取帧")
                break
            
            frame_count += 1
            
            # 在帧上显示信息
            text = f"Frame: {frame_count} | Press 'q' to quit"
            cv2.putText(frame, text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Camera Test', frame)
            
            # 按键检测
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # q 或 ESC
                break
                
    except KeyboardInterrupt:
        print("\n已中断")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"总共显示了 {frame_count} 帧")


def main():
    print("========================================")
    print("虚拟摄像头测试工具")
    print("========================================\n")
    
    cameras = list_cameras()
    
    if not cameras:
        print("未找到任何摄像头设备")
        print("\n如果你正在运行虚拟摄像头，请确保:")
        print("1. 已安装 OBS Studio")
        print("2. 虚拟摄像头程序正在运行")
        print("3. 没有其他程序占用摄像头")
        return
    
    print(f"找到 {len(cameras)} 个摄像头设备\n")
    
    # 如果指定了摄像头索引
    if len(sys.argv) > 1:
        camera_index = int(sys.argv[1])
    else:
        # 提示用户选择
        if len(cameras) == 1:
            camera_index = cameras[0]['index']
            print(f"自动选择摄像头 {camera_index}\n")
        else:
            print("请选择要测试的摄像头:")
            for cam in cameras:
                print(f"  {cam['index']} - {cam['width']}x{cam['height']} @ {cam['fps']} FPS")
            
            try:
                camera_index = int(input("\n输入摄像头编号: "))
            except ValueError:
                print("无效的输入")
                return
    
    # 测试摄像头
    test_camera(camera_index)


if __name__ == '__main__':
    main()


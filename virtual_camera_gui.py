#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 虚拟摄像头程序 - GUI版本
带图形界面的虚拟摄像头控制程序
"""

import cv2
import pyvirtualcam
import numpy as np
import time
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class VirtualCameraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("虚拟摄像头控制器")
        self.root.geometry("600x400")
        
        self.video_path = None
        self.is_running = False
        self.camera_thread = None
        self.cap = None
        self.stop_flag = False
        self.playing = False  # 是否正在播放视频
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="Windows 虚拟摄像头", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # 视频选择
        video_frame = ttk.LabelFrame(self.root, text="视频文件", padding="10")
        video_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.video_label = ttk.Label(video_frame, text="未选择视频文件", 
                                     foreground="gray")
        self.video_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        select_btn = ttk.Button(video_frame, text="选择视频", 
                               command=self.select_video)
        select_btn.pack(side=tk.RIGHT)
        
        # 设置选项
        settings_frame = ttk.LabelFrame(self.root, text="输出设置", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 分辨率
        res_frame = ttk.Frame(settings_frame)
        res_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(res_frame, text="分辨率:", width=10).pack(side=tk.LEFT)
        
        self.width_var = tk.StringVar(value="1280")
        width_combo = ttk.Combobox(res_frame, textvariable=self.width_var, 
                                   values=["640", "1280", "1920"], width=8)
        width_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(res_frame, text="x").pack(side=tk.LEFT)
        
        self.height_var = tk.StringVar(value="720")
        height_combo = ttk.Combobox(res_frame, textvariable=self.height_var,
                                    values=["480", "720", "1080"], width=8)
        height_combo.pack(side=tk.LEFT, padx=5)
        
        # 帧率
        fps_frame = ttk.Frame(settings_frame)
        fps_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(fps_frame, text="帧率:", width=10).pack(side=tk.LEFT)
        
        self.fps_var = tk.StringVar(value="30")
        fps_combo = ttk.Combobox(fps_frame, textvariable=self.fps_var,
                                values=["15", "24", "30", "60"], width=8)
        fps_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(fps_frame, text="FPS").pack(side=tk.LEFT)
        
        # 控制按钮
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="启动虚拟摄像头", 
                                    command=self.start_camera, 
                                    style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.play_btn = ttk.Button(control_frame, text="开始播放", 
                                   command=self.start_playing,
                                   state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_btn = ttk.Button(control_frame, text="停止", 
                                   command=self.stop_camera,
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 状态显示
        status_frame = ttk.LabelFrame(self.root, text="状态", padding="10")
        status_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, state=tk.DISABLED,
                                   wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.status_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        self.log("程序已启动，请选择视频文件")
        
    def select_video(self):
        """选择视频文件"""
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            self.video_path = filename
            self.video_label.config(text=Path(filename).name, foreground="black")
            self.log(f"已选择视频: {Path(filename).name}")
            
            # 显示视频信息
            cap = cv2.VideoCapture(filename)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frames / fps if fps > 0 else 0
                
                self.log(f"  分辨率: {width}x{height}")
                self.log(f"  帧率: {fps:.2f} FPS")
                self.log(f"  时长: {duration:.2f} 秒")
                cap.release()
    
    def start_camera(self):
        """启动虚拟摄像头"""
        if not self.video_path:
            messagebox.showwarning("警告", "请先选择视频文件")
            return
        
        if not Path(self.video_path).exists():
            messagebox.showerror("错误", "视频文件不存在")
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            fps = int(self.fps_var.get())
        except ValueError:
            messagebox.showerror("错误", "分辨率或帧率格式不正确")
            return
        
        self.is_running = True
        self.stop_flag = False
        self.playing = False
        self.start_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.log("正在启动虚拟摄像头...")
        
        # 在新线程中运行摄像头
        self.camera_thread = threading.Thread(
            target=self.run_camera,
            args=(width, height, fps),
            daemon=True
        )
        self.camera_thread.start()
    
    def start_playing(self):
        """开始播放视频"""
        if self.is_running and not self.playing:
            self.playing = True
            self.play_btn.config(state=tk.DISABLED)
            self.log("=== 开始播放视频 ===")
    
    def stop_camera(self):
        """停止虚拟摄像头"""
        self.log("正在停止虚拟摄像头...")
        self.stop_flag = True
        self.is_running = False
        self.playing = False
        
        if self.cap:
            self.cap.release()
        
        self.start_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("虚拟摄像头已停止")
    
    def create_standby_frame(self, width, height):
        """创建待机画面"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # 设置深色背景
        frame[:, :] = (30, 30, 30)
        
        # 添加文字
        texts = [
            ("虚拟摄像头已就绪", (255, 255, 255), 2.0 if width >= 1280 else 1.2, -120),
            ("等待开始播放...", (200, 200, 200), 1.2 if width >= 1280 else 0.8, -40),
        ]
        
        for text, color, scale, y_offset in texts:
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = int(scale * 2)
            
            # 获取文字大小
            (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)
            
            # 计算居中位置
            x = (width - text_width) // 2
            y = (height // 2) + y_offset
            
            # 添加阴影
            cv2.putText(frame, text, (x + 3, y + 3), font, scale, (0, 0, 0), thickness)
            # 添加主文字
            cv2.putText(frame, text, (x, y), font, scale, color, thickness)
        
        # 添加提示信息
        hint_text = "在GUI中点击 '开始播放' 按钮"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.7 if width >= 1280 else 0.5
        thickness = 1
        (text_width, text_height), _ = cv2.getTextSize(hint_text, font, scale, thickness)
        x = (width - text_width) // 2
        y = height - 50
        cv2.putText(frame, hint_text, (x, y), font, scale, (150, 150, 150), thickness)
        
        return frame
    
    def run_camera(self, width, height, fps):
        """运行虚拟摄像头（在独立线程中）"""
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            
            with pyvirtualcam.Camera(width=width, height=height, 
                                     fps=fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
                self.log(f"虚拟摄像头已启动: {cam.device}")
                self.log(f"输出: {width}x{height} @ {fps} FPS")
                self.log("=== 待机模式 ===")
                self.log("虚拟摄像头已就绪，显示待机画面")
                self.log("点击 '开始播放' 按钮开始播放视频")
                
                frame_time = 1.0 / fps
                frame_count = 0
                standby_frame = self.create_standby_frame(width, height)
                
                while not self.stop_flag:
                    start_time = time.time()
                    
                    # 如果还未开始播放，显示待机画面
                    if not self.playing:
                        cam.send(standby_frame)
                        cam.sleep_until_next_frame()
                        continue
                    
                    # 开始播放视频
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        # 重新开始播放
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                        
                        if not ret:
                            self.log("错误：无法读取视频帧")
                            break
                        
                        self.log("视频循环播放")
                    
                    # 调整帧大小
                    if frame.shape[1] != width or frame.shape[0] != height:
                        frame = cv2.resize(frame, (width, height))
                    
                    # 发送到虚拟摄像头
                    cam.send(frame)
                    
                    frame_count += 1
                    if frame_count % 300 == 0:  # 每10秒（30fps）更新一次
                        self.log(f"已播放 {frame_count} 帧")
                    
                    # 控制帧率
                    elapsed = time.time() - start_time
                    sleep_time = frame_time - elapsed
                    if sleep_time > 0:
                        cam.sleep_until_next_frame()
                        
        except Exception as e:
            self.log(f"错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            if self.cap:
                self.cap.release()
            self.root.after(0, self.stop_camera)
    
    def log(self, message):
        """在状态文本框中显示日志"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)


def main():
    """主函数"""
    root = tk.Tk()
    app = VirtualCameraGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()


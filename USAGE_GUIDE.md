# 虚拟摄像头使用指南

## 快速开始

### Windows用户（推荐方式）

1. **下载并安装 OBS Studio**
   - 访问 https://obsproject.com/download
   - 下载 Windows 版本
   - 运行安装程序（会自动安装虚拟摄像头驱动）

2. **安装Python依赖**
   - 双击运行 `install_windows.bat`
   - 或手动执行：`pip install -r requirements.txt`

3. **启动虚拟摄像头**

   **方式A：图形界面（最简单）**
   ```bash
   # 双击运行
   run_gui.bat
   
   # 或使用命令行
   python virtual_camera_gui.py
   ```

   **方式B：命令行**
   ```bash
   python virtual_camera.py your_video.mp4
   ```

## 详细使用说明

### 1. 创建测试视频

如果你没有视频文件，可以生成一个测试视频：

```bash
python create_test_video.py
```

这会创建一个名为 `test_video.mp4` 的10秒测试视频。

自定义测试视频：
```bash
python create_test_video.py --duration 30 --width 1920 --height 1080 --fps 60
```

### 2. 测试摄像头

在使用虚拟摄像头之前，可以测试系统中的摄像头：

```bash
python test_camera.py
```

这个工具会：
- 列出所有可用的摄像头
- 让你选择要测试的摄像头
- 打开预览窗口显示摄像头画面

### 3. 运行虚拟摄像头

#### 图形界面版本

```bash
python virtual_camera_gui.py
```

GUI界面提供：
- 视频文件选择器
- 分辨率设置（640x480, 1280x720, 1920x1080）
- 帧率设置（15, 24, 30, 60 FPS）
- 启动/停止按钮
- 实时状态显示

#### 命令行版本

基本用法：
```bash
python virtual_camera.py video.mp4
```

自定义参数：
```bash
# 指定分辨率和帧率
python virtual_camera.py video.mp4 --width 1920 --height 1080 --fps 60

# 较低配置（节省CPU）
python virtual_camera.py video.mp4 --width 640 --height 480 --fps 15
```

参数说明：
- `video`: 视频文件路径（必需）
- `--width`: 输出宽度（默认1280）
- `--height`: 输出高度（默认720）
- `--fps`: 输出帧率（默认30）

### 4. 在应用程序中使用虚拟摄像头

启动虚拟摄像头后，在其他应用中使用：

#### Zoom
1. 打开 Zoom
2. 设置 -> 视频
3. 摄像头选择 "OBS Virtual Camera"

#### Microsoft Teams
1. 打开 Teams
2. 设置 -> 设备
3. 摄像头选择 "OBS Virtual Camera"

#### Skype
1. 打开 Skype
2. 设置 -> 音频和视频
3. 摄像头选择 "OBS Virtual Camera"

#### Google Meet / Discord / 其他
- 在视频设置中查找并选择 "OBS Virtual Camera"

### 5. 停止虚拟摄像头

- GUI版本：点击"停止"按钮
- 命令行版本：按 `Ctrl+C`

## 常见使用场景

### 场景1：在线会议播放PPT讲解视频

```bash
# 录制好讲解视频后
python virtual_camera.py presentation.mp4 --width 1920 --height 1080
```

在会议软件中选择虚拟摄像头，即可播放你的讲解视频。

### 场景2：游戏直播/演示

```bash
# 播放游戏录像
python virtual_camera.py gameplay.mp4
```

### 场景3：测试视频会议效果

```bash
# 生成测试视频
python create_test_video.py --duration 60

# 播放测试视频
python virtual_camera.py test_video.mp4
```

### 场景4：循环播放宣传视频

```bash
# 视频会自动循环播放
python virtual_camera.py promo_video.mp4
```

## 性能优化建议

### CPU使用率过高？

1. **降低分辨率**
   ```bash
   python virtual_camera.py video.mp4 --width 640 --height 480
   ```

2. **降低帧率**
   ```bash
   python virtual_camera.py video.mp4 --fps 15
   ```

3. **使用低比特率视频**
   - 推荐使用 H.264 编码的 MP4 文件
   - 避免使用超高清视频

### 画面卡顿？

1. 确保视频文件在本地硬盘（不在网络驱动器）
2. 关闭不必要的后台程序
3. 降低输出分辨率和帧率

### 同步问题？

如果音视频不同步：
- 虚拟摄像头只传输视频，不传输音频
- 音频需要单独通过虚拟音频设备传输
- 或使用OBS Studio的完整功能

## 高级技巧

### 1. 多个视频源切换

可以创建多个批处理文件：

**video1.bat**
```batch
@echo off
python virtual_camera.py video1.mp4
```

**video2.bat**
```batch
@echo off
python virtual_camera.py video2.mp4
```

### 2. 定时启动

使用Windows任务计划程序设置定时启动虚拟摄像头。

### 3. 与OBS配合使用

虚拟摄像头可以作为OBS的一个源：
1. OBS添加"视频捕获设备"
2. 选择虚拟摄像头设备
3. OBS再输出到另一个虚拟摄像头

## 故障排除

### 问题1：找不到虚拟摄像头设备

**解决方法：**
1. 确认已安装OBS Studio
2. 打开OBS -> 工具 -> 虚拟摄像头
3. 点击"启动"测试虚拟摄像头
4. 重启计算机

### 问题2：其他程序无法识别虚拟摄像头

**解决方法：**
1. 重启相关应用程序
2. 检查应用程序权限（摄像头访问权限）
3. Windows设置 -> 隐私 -> 摄像头，确保允许应用访问

### 问题3：程序提示 "No module named 'pyvirtualcam'"

**解决方法：**
```bash
pip install pyvirtualcam
```

### 问题4：程序提示 "No module named 'cv2'"

**解决方法：**
```bash
pip install opencv-python
```

### 问题5：视频播放画面倒置

这通常不会发生，但如果出现：
- 检查视频文件是否正常
- 尝试用其他播放器播放视频确认

### 问题6：无法打开视频文件

**解决方法：**
1. 确认视频文件路径正确
2. 确认视频格式受支持
3. 尝试用VLC等播放器打开视频测试
4. 转换视频格式为MP4：
   ```bash
   ffmpeg -i input.avi -c:v libx264 output.mp4
   ```

## 技术支持

如有问题：
1. 查看 `README.md` 中的常见问题
2. 检查系统要求是否满足
3. 确认所有依赖已正确安装

## 注意事项

⚠️ **重要提示**
- 虚拟摄像头运行时会占用一定CPU资源
- 不要在虚拟摄像头程序中播放受版权保护的内容
- 某些会议软件可能检测虚拟摄像头并禁用
- 建议在使用前测试兼容性

## 许可证

本项目使用 MIT 许可证。


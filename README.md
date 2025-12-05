# Windows 虚拟摄像头程序

这个程序可以在Windows系统上创建一个虚拟摄像头设备，循环播放指定的视频文件。

## 功能特点

- ✅ 模拟真实摄像头设备
- ✅ 支持常见视频格式（MP4, AVI, MOV等）
- ✅ **待机模式** - 启动后显示待机画面，等待用户手动开始播放
- ✅ 自动循环播放
- ✅ 可自定义分辨率和帧率
- ✅ 兼容所有调用摄像头的应用程序（Zoom, Teams, Skype等）

## 系统要求

- Windows 10/11
- Python 3.7+
- OBS Studio（提供虚拟摄像头驱动）

## 安装步骤

### 1. 安装 OBS Studio

首先需要安装 OBS Studio 来提供虚拟摄像头驱动：

1. 访问 https://obsproject.com/download
2. 下载并安装 OBS Studio for Windows
3. 安装后不需要运行OBS，驱动会自动安装

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install opencv-python pyvirtualcam numpy
```

## 使用方法

### 基本使用（默认：等待模式）

```bash
# 启动后显示待机画面，按Enter开始播放
python virtual_camera.py video.mp4
```

程序会先显示待机画面，等待你：
1. 打开Zoom/Teams等应用，选择虚拟摄像头
2. 在命令行窗口按 **Enter键** 开始播放视频

### 自定义参数

```bash
# 指定分辨率和帧率
python virtual_camera.py video.mp4 --width 1920 --height 1080 --fps 60

# 禁用等待模式，立即播放（旧行为）
python virtual_camera.py video.mp4 --no-wait

# 播放不同视频
python virtual_camera.py demo.avi --fps 30
```

### 命令行参数

- `video`: 视频文件路径（必需）
- `--width`: 输出宽度（默认: 1280）
- `--height`: 输出高度（默认: 720）
- `--fps`: 输出帧率（默认: 30）
- `--no-wait`: 禁用等待模式，立即播放视频

## 使用示例

### 示例1：在会议软件中使用（推荐流程）

1. 运行虚拟摄像头程序（待机模式）：
   ```bash
   python virtual_camera.py my_video.mp4
   ```
   此时会显示"虚拟摄像头已就绪"的待机画面

2. 打开会议软件（Zoom/Teams/Skype等）

3. 在摄像头设置中选择 "OBS Virtual Camera"
   - 此时会议中会看到待机画面，而不是直接播放视频

4. **准备好后**，在命令行窗口按 **Enter键** 开始播放视频
   - 或在GUI版本中点击"开始播放"按钮

5. 会议中将显示你的视频内容

### 示例2：测试虚拟摄像头

使用Windows自带的相机应用测试：

1. 运行虚拟摄像头程序
2. 打开"相机"应用（Windows Camera）
3. 点击切换摄像头按钮，选择虚拟摄像头
4. 应该能看到视频播放

## 停止程序

按 `Ctrl+C` 停止虚拟摄像头

## 常见问题

### Q: 提示找不到虚拟摄像头设备

**A:** 确保已正确安装 OBS Studio。安装后重启电脑。

### Q: 其他程序看不到虚拟摄像头

**A:** 
1. 检查OBS是否正确安装
2. 在OBS中点击"工具" -> "虚拟摄像头" 确认驱动已安装
3. 重启相关应用程序

### Q: 视频播放卡顿

**A:** 
1. 降低输出分辨率：`--width 640 --height 480`
2. 降低帧率：`--fps 15`
3. 确保视频文件不是太大

### Q: 支持哪些视频格式？

**A:** 支持OpenCV能够读取的所有格式：
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)

## 高级用法

### 创建 GUI 版本

如果你想要图形界面版本，可以运行：

```bash
python virtual_camera_gui.py
```

### 多个虚拟摄像头

要运行多个虚拟摄像头实例，需要安装额外的虚拟摄像头驱动。

## 技术原理

程序使用以下技术：
- **pyvirtualcam**: 与虚拟摄像头驱动通信
- **OpenCV**: 读取和处理视频文件
- **OBS Virtual Camera**: 提供Windows虚拟摄像头驱动

## 注意事项

⚠️ **使用限制**
- 只能在Windows系统使用
- 需要先安装OBS Studio
- 某些视频会议软件可能有虚拟摄像头检测机制

⚠️ **性能建议**
- 高分辨率视频会占用更多CPU
- 建议使用H.264编码的MP4文件
- 较低的帧率可以节省资源

## License

MIT License


# 使用示例

## 基本示例

### 示例1：等待模式（推荐）⭐

最常用的方式，适合会议演讲：

```bash
# 启动虚拟摄像头
python virtual_camera.py presentation.mp4
```

**流程：**
1. 程序启动，显示待机画面 ✓
2. 打开Zoom，选择"OBS Virtual Camera" ✓
3. 待机画面显示在会议中 ✓
4. 准备好后，回到命令行窗口
5. 按 **Enter键** 开始播放 ✓

---

### 示例2：立即播放模式

适合测试或自动化场景：

```bash
# 禁用等待模式，立即播放
python virtual_camera.py video.mp4 --no-wait
```

**流程：**
1. 程序启动，视频立即播放
2. 打开应用，选择虚拟摄像头
3. 看到正在播放的视频

---

### 示例3：GUI版本（最简单）🎨

图形界面操作：

```bash
python virtual_camera_gui.py
```

**步骤：**
1. 点击"选择视频"，选择视频文件
2. 设置分辨率和帧率（可选）
3. 点击"启动虚拟摄像头" → 待机画面出现
4. 打开Zoom等应用，选择虚拟摄像头
5. 准备好后，点击"开始播放"按钮
6. 视频开始播放

---

## 高级示例

### 示例4：高清会议演示

```bash
# 1080p @ 30fps
python virtual_camera.py demo.mp4 --width 1920 --height 1080 --fps 30
```

适合：
- 产品演示
- 技术分享
- 教学视频

---

### 示例5：低配置模式（省电）

```bash
# 480p @ 15fps
python virtual_camera.py video.mp4 --width 640 --height 480 --fps 15
```

适合：
- 笔记本电脑
- 长时间运行
- 网络带宽有限

---

### 示例6：创建测试视频

如果没有视频文件：

```bash
# 生成10秒测试视频
python create_test_video.py

# 生成30秒高清测试视频
python create_test_video.py --duration 30 --width 1920 --height 1080

# 使用测试视频
python virtual_camera.py test_video.mp4
```

---

### 示例7：测试摄像头

检查虚拟摄像头是否正常：

```bash
python test_camera.py
```

会列出所有可用摄像头并打开预览窗口。

---

## 实战场景

### 场景A：在线会议中播放PPT讲解视频

**准备工作：**
```bash
# 录制好讲解视频（使用OBS或其他录屏软件）
# 保存为 presentation.mp4
```

**会议当天：**
```bash
# 1. 会议前5分钟启动
python virtual_camera.py presentation.mp4 --width 1920 --height 1080

# 2. 打开Zoom，进入会议室

# 3. 在Zoom中选择：
#    视频设置 → OBS Virtual Camera

# 4. 此时会议中显示待机画面

# 5. 轮到你演讲时，按Enter键开始播放
```

**优点：**
- ✅ 不会错过视频开头
- ✅ 可以提前调试好摄像头
- ✅ 专业的呈现效果

---

### 场景B：教学课堂播放演示视频

**老师端：**
```bash
# 使用GUI版本，更方便控制
python virtual_camera_gui.py
```

**步骤：**
1. 课前启动GUI，选择今天要播放的视频
2. 启动虚拟摄像头（显示待机画面）
3. 打开在线教室（Teams/Zoom）
4. 学生看到待机画面
5. 讲解完理论后，点击"开始播放"按钮
6. 播放演示视频
7. 视频结束后（自动循环），可以讲解
8. 需要再看一遍时，视频已经循环播放了

---

### 场景C：游戏录像展示

```bash
# 播放游戏录像
python virtual_camera.py gameplay.mp4

# 在Discord/OBS中选择虚拟摄像头
# 按Enter开始播放
```

---

### 场景D：循环播放宣传视频

适合展台、直播预热等：

```bash
# 启动后立即播放（循环）
python virtual_camera.py promo.mp4 --no-wait

# 视频会一直循环播放
# Ctrl+C 停止
```

---

## 常见组合

### 组合1：标准会议配置

```bash
python virtual_camera.py video.mp4 \
  --width 1280 \
  --height 720 \
  --fps 30
```

平衡画质和性能。

---

### 组合2：极致画质配置

```bash
python virtual_camera.py video.mp4 \
  --width 1920 \
  --height 1080 \
  --fps 60
```

需要强大的CPU和网络带宽。

---

### 组合3：省电模式

```bash
python virtual_camera.py video.mp4 \
  --width 640 \
  --height 480 \
  --fps 15 \
  --no-wait
```

最低资源占用。

---

## 批处理脚本示例

### Windows批处理文件

**start_presentation.bat**
```batch
@echo off
echo 正在启动演示视频...
python virtual_camera.py presentation.mp4 --width 1920 --height 1080
pause
```

**start_low_quality.bat**
```batch
@echo off
echo 正在启动（低配置模式）...
python virtual_camera.py video.mp4 --width 640 --height 480 --fps 15
pause
```

---

## 故障排除示例

### 测试虚拟摄像头是否正常

```bash
# 1. 列出所有摄像头
python test_camera.py

# 2. 应该能看到多个摄像头设备
# 找到 OBS Virtual Camera

# 3. 如果找不到，检查OBS是否安装
```

---

### 测试视频文件是否可用

```bash
# 尝试立即播放模式
python virtual_camera.py test.mp4 --no-wait

# 如果能正常播放，说明视频文件正常
# 如果报错，检查视频格式
```

---

## 对比示例

### 等待模式 vs 立即播放

**等待模式：**
```bash
python virtual_camera.py video.mp4
# 启动 → 待机画面 → 按Enter → 播放
```

**立即播放：**
```bash
python virtual_camera.py video.mp4 --no-wait
# 启动 → 立即播放
```

**选择建议：**
- 会议演讲 → 用等待模式 ✓
- 自动化测试 → 用立即播放 ✓
- 不确定 → 用等待模式（默认）✓

---

## 小技巧

### 技巧1：多视频快速切换

创建多个批处理文件：

**video1.bat**
```batch
python virtual_camera.py video1.mp4
```

**video2.bat**
```batch
python virtual_camera.py video2.mp4
```

需要切换时：
1. Ctrl+C 停止当前视频
2. 运行另一个bat文件

---

### 技巧2：预先生成待机画面预览

```bash
# 启动虚拟摄像头
python virtual_camera.py video.mp4

# 打开Windows相机应用
# 切换到虚拟摄像头
# 查看待机画面效果
```

---

### 技巧3：同时运行多个虚拟摄像头？

**不可以！** OBS Virtual Camera同时只能被一个程序使用。

如需多个虚拟摄像头，需要安装额外的虚拟摄像头驱动（如ManyCam）。

---

## 总结

记住三个最常用的命令：

```bash
# 1. 等待模式（推荐）
python virtual_camera.py video.mp4

# 2. GUI版本（最简单）
python virtual_camera_gui.py

# 3. 立即播放（测试用）
python virtual_camera.py video.mp4 --no-wait
```

更多帮助，查看：
- README.md - 完整文档
- WAIT_MODE_GUIDE.md - 等待模式详解
- USAGE_GUIDE.md - 详细使用指南


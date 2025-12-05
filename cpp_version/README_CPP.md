# Windows 虚拟摄像头 - C++ DirectShow 版本

这是一个使用C++和DirectShow实现的高性能虚拟摄像头程序。

## ⚠️ 注意

**C++版本实现比较复杂，需要深入了解DirectShow框架。**

对于大多数用户，我们**强烈推荐使用Python版本**（更简单、更易用）。

## 技术要求

1. **开发环境**
   - Visual Studio 2019 或更高版本
   - Windows SDK 10
   - DirectShow BaseClasses

2. **依赖库**
   - OpenCV 4.x
   - DirectShow SDK

## 为什么C++版本很复杂？

DirectShow虚拟摄像头实现需要：

1. **编写COM组件**
   - 实现IUnknown接口
   - 注册CLSID到注册表
   - 实现类工厂

2. **实现DirectShow过滤器**
   - CSource基类
   - CSourceStream基类
   - 媒体类型协商
   - 内存分配器管理

3. **系统注册**
   - 注册为系统设备
   - 创建设备INF文件
   - 可能需要驱动签名

4. **调试困难**
   - COM组件调试复杂
   - 需要GraphEdit等工具

## 推荐方案

### 方案1：使用Python版本（最简单）✅

```bash
pip install pyvirtualcam opencv-python
python virtual_camera.py video.mp4
```

**优点：**
- 简单易用
- 跨平台
- 维护方便
- 功能完整

### 方案2：使用OBS Studio（专业）

直接使用OBS Studio的虚拟摄像头功能：
1. 安装OBS Studio
2. 添加"媒体源"，选择视频文件
3. 启动"虚拟摄像头"

**优点：**
- 专业级工具
- 功能强大
- UI友好
- 稳定可靠

### 方案3：C++实现（仅供学习）

如果你确实需要C++实现（例如学习DirectShow或特殊性能需求），完整实现需要：

1. **参考项目**
   - [DirectShow虚拟摄像头示例](https://github.com/rdp/screen-capture-recorder-to-video-windows-free)
   - [vcam](https://github.com/xland/vcam)

2. **学习资源**
   - DirectShow官方文档
   - "Programming Microsoft DirectShow" 书籍

## 编译C++版本（高级）

如果你坚持要编译C++版本：

### 步骤1：安装依赖

```bash
# 安装OpenCV
vcpkg install opencv:x64-windows

# 下载DirectShow BaseClasses
# 从 Windows SDK 中复制 BaseClasses 源码
```

### 步骤2：编译BaseClasses

```bash
cd "C:\Program Files (x86)\Windows Kits\10\Samples\...\BaseClasses"
# 使用VS编译strmbase.lib
```

### 步骤3：编译项目

```bash
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

### 步骤4：注册过滤器

```bash
regsvr32 virtual_camera.dll
```

## 总结

| 方案 | 难度 | 开发时间 | 推荐度 |
|------|------|----------|--------|
| Python (pyvirtualcam) | ⭐ | 1小时 | ⭐⭐⭐⭐⭐ |
| OBS Studio | ⭐ | 5分钟 | ⭐⭐⭐⭐ |
| C++ DirectShow | ⭐⭐⭐⭐⭐ | 1-2周 | ⭐ |

**建议：使用Python版本！**

除非你有特殊需求（如嵌入到其他C++项目、极致性能要求），否则Python版本是最佳选择。


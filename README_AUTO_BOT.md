# 🤖 自动学习机器人使用指南

## 功能特性

✅ **自动截屏** - 自动截取二级菜单区域  
✅ **OCR识别** - 识别"x.x/x.x学时"格式文本  
✅ **智能判断** - 自动比较左右数字  
✅ **自动点击** - 点击未完成的课程  
✅ **日志记录** - 记录所有操作过程  

---

## 📦 安装依赖

### 方法1：完整安装（推荐）

```bash
# 安装Python依赖
pip install pyautogui pytesseract pillow opencv-python

# 安装系统OCR引擎
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS:
brew install tesseract tesseract-lang

# Windows:
# 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki
```

### 方法2：最小安装（仅截图）

```bash
# 只能截图，不能自动识别
pip install pyautogui pillow opencv-python
```

---

## 🚀 使用方法

### 方式A：完整版机器人（推荐）

```bash
# 处理所有菜单
python auto_learning_bot.py

# 只处理指定菜单
python auto_learning_bot.py --menu 1 2

# 测试模式（不等待视频播放）
python auto_learning_bot.py --test

# 指定基准图片
python auto_learning_bot.py --base-image lists.png
```

**参数说明：**
- `--menu 1 2 3` - 只处理菜单1, 2, 3
- `--test` - 测试模式，不等待视频
- `--base-image` - 指定用于定位窗口的图片

### 方式B：简易版机器人

```bash
python quick_start_bot.py
```

**适合场景：**
- 快速测试
- 只需要截图
- 不需要复杂配置

---

## 📋 使用流程

### 步骤1：准备工作

1. 打开浏览器，进入课程页面
2. 确保课程列表在屏幕上可见
3. 不要最小化窗口

### 步骤2：运行程序

```bash
python auto_learning_bot.py --test
```

### 步骤3：定位窗口

程序启动后会：
- 方案A：自动在屏幕上查找 `lists.png`
- 方案B：提示你将鼠标移到列表左上角

### 步骤4：自动执行

程序会自动：
1. ✅ 点击一级菜单（红色按钮）
2. ✅ 截取二级菜单区域
3. ✅ OCR识别学时信息
4. ✅ 判断是否未完成
5. ✅ 点击未完成课程
6. ✅ 等待视频播放（可选）
7. ✅ 返回继续处理

---

## 📸 自动截屏功能

### 截图保存

程序会自动保存截图：
```
screenshot_menu1_143025.png  # 菜单1，14:30:25截图
screenshot_menu2_143028.png  # 菜单2，14:30:28截图
screenshot_menu3_143031.png  # 菜单3，14:30:31截图
screenshot_menu4_143034.png  # 菜单4，14:30:34截图
```

### 截图区域

自动计算每个菜单的二级区域：
- 菜单1: Y=305~428 (高度123px)
- 菜单2: Y=494~617 (高度123px)
- 菜单3: Y=685~808 (高度123px)
- 菜单4: Y=875~970 (高度95px)

---

## 🔍 OCR识别示例

### 识别过程

```python
# 1. 截取区域
screenshot = capture_region(50, 305, 500, 123)

# 2. 预处理（灰度化、二值化）
gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# 3. OCR识别
text = pytesseract.image_to_string(binary, lang='chi_sim+eng')

# 4. 正则提取
pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
matches = re.findall(pattern, text)

# 5. 判断
for completed, total in matches:
    if float(completed) < float(total):
        print(f"未完成: {completed}/{total}学时")
```

### 识别结果示例

```
OCR识别文本: 
  课程一 0.0/2.0学时
  课程二 1.5/2.0学时
  课程三 2.0/2.0学时

提取结果:
  ✅ 课程1: 0.0/2.0学时 - ❌ 未完成
  ✅ 课程2: 1.5/2.0学时 - ❌ 未完成  
  ✅ 课程3: 2.0/2.0学时 - ✅ 已完成

需要点击: 课程1, 课程2
```

---

## 📊 日志文件

### 自动生成日志

每次运行都会生成日志文件：
```
learning_log_20241205_143015.txt
```

### 日志内容

```
[2024-12-05 14:30:15] 🎓 自动学习机器人启动
[2024-12-05 14:30:15] 正在查找课程列表窗口...
[2024-12-05 14:30:16] ✅ 找到窗口位置: (100, 200)
[2024-12-05 14:30:19] 处理一级菜单 1
[2024-12-05 14:30:19] 步骤1: 点击一级菜单展开
[2024-12-05 14:30:21] 步骤2: 等待二级菜单展开...
[2024-12-05 14:30:22] 步骤3: 截图并分析学时信息
[2024-12-05 14:30:23]    OCR识别文本: 课程一 0.0/2.0学时...
[2024-12-05 14:30:23]    找到 2 个课程:
[2024-12-05 14:30:23]    课程 1: 0.0/2.0学时 - ❌ 未完成
[2024-12-05 14:30:23]    课程 2: 1.5/2.0学时 - ❌ 未完成
[2024-12-05 14:30:23] 步骤4: 处理 2 个未完成课程
[2024-12-05 14:30:24]    >>> 学习课程: 0.0/2.0学时
[2024-12-05 14:30:24]    点击: (250, 530)
[2024-12-05 14:30:27]    等待视频加载...
[2024-12-05 14:30:30]    预计学习时长: 120 秒
[2024-12-05 14:30:30] ✅ 自动学习完成
```

---

## 🎯 工作原理

### 流程图

```
┌─────────────────────────────────────┐
│  1. 查找窗口位置                     │
│     pyautogui.locateOnScreen()     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. 点击一级菜单                     │
│     click(665, 271)                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. 截取二级菜单区域                 │
│     ImageGrab.grab(bbox)           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  4. OCR识别文本                      │
│     pytesseract.image_to_string()  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  5. 正则提取学时                     │
│     re.findall(r'(\d+\.?\d*)/...')│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  6. 判断是否未完成                   │
│     if completed < total           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  7. 点击未完成课程                   │
│     click(estimated_position)      │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  8. 等待播放完成                     │
│     time.sleep() or 检测完成标志    │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  9. 返回列表，处理下一个             │
│     pyautogui.press('esc')         │
└─────────────────────────────────────┘
```

---

## 💡 高级配置

### 自定义菜单坐标

编辑 `auto_learning_bot.py`:

```python
self.level1_menus = [
    {'id': 1, 'x': 665, 'y': 271},  # 修改这里
    {'id': 2, 'x': 665, 'y': 461},
    # ...
]
```

### 自定义二级区域

```python
self.level2_regions = {
    1: {'x': 50, 'y': 305, 'width': 500, 'height': 123},
    # ...
}
```

### 调整等待时间

```python
# 点击后等待
self.click_point(x, y, delay=1.5)  # 改为2.0更保守

# 视频播放等待
video_duration = int(course['total'] * 60)  # 1学时=60秒
```

---

## ⚠️ 常见问题

### Q1: OCR识别不准确

**解决：**
```bash
# 1. 确认语言包安装
tesseract --list-langs

# 2. 应该看到 chi_sim (简体中文)

# 3. 如果没有，安装：
sudo apt-get install tesseract-ocr-chi-sim
```

### Q2: 找不到窗口

**解决：**
```python
# 方案A: 使用手动定位
# 程序会提示移动鼠标到左上角

# 方案B: 调整confidence
location = pyautogui.locateOnScreen('lists.png', confidence=0.5)
```

### Q3: 点击位置不准

**解决：**
```python
# 1. 先点击一级菜单
# 2. 手动截图
# 3. 查看实际课程位置
# 4. 修改click_incomplete_course()中的坐标
```

### Q4: 截图全黑或错误

**解决：**
```python
# Linux X11权限问题
import os
os.environ['DISPLAY'] = ':0'

# 或使用root权限
sudo python auto_learning_bot.py
```

---

## 📈 性能优化

### 提高识别速度

```python
# 1. 使用更快的OCR模式
config = '--oem 1 --psm 6'  # 使用LSTM引擎

# 2. 减小截图尺寸
screenshot = screenshot.resize((width//2, height//2))

# 3. 只识别数字和符号
config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789./'
```

### 减少等待时间

```python
# 使用更短的等待
delay=0.5  # 而不是1.5

# 异步处理
import threading
# 在等待时处理其他任务
```

---

## 🎓 使用技巧

### 技巧1：批量测试

```bash
# 只测试菜单1
python auto_learning_bot.py --menu 1 --test

# 测试通过后，处理所有
python auto_learning_bot.py
```

### 技巧2：分段执行

```bash
# 今天处理菜单1和2
python auto_learning_bot.py --menu 1 2

# 明天处理菜单3和4
python auto_learning_bot.py --menu 3 4
```

### 技巧3：后台运行

```bash
# Linux后台运行
nohup python auto_learning_bot.py > output.log 2>&1 &

# 查看日志
tail -f learning_log_*.txt
```

---

## ✅ 完整示例

### 示例1：首次使用

```bash
# 1. 安装依赖
pip install pyautogui pytesseract pillow opencv-python

# 2. 测试运行
python auto_learning_bot.py --menu 1 --test

# 3. 查看截图
ls screenshot_*.png

# 4. 查看日志
cat learning_log_*.txt

# 5. 正式运行
python auto_learning_bot.py
```

### 示例2：无OCR使用

```bash
# 只截图，手动查看
python quick_start_bot.py

# 查看生成的截图
ls menu_*_screenshot.png

# 手动识别学时，然后手动点击
```

---

## 📞 故障排除

如果遇到问题：

1. ✅ 查看日志文件
2. ✅ 检查截图是否正确
3. ✅ 验证OCR安装
4. ✅ 测试单个菜单
5. ✅ 调整坐标参数

---

## 🎉 总结

**完整版机器人** (`auto_learning_bot.py`)
- ✅ 功能完整
- ✅ 自动化程度高
- ✅ 详细日志
- ✅ 适合长期使用

**简易版机器人** (`quick_start_bot.py`)
- ✅ 快速启动
- ✅ 简单易用
- ✅ 适合测试

**推荐流程：**
1. 先用简易版测试截图
2. 确认能正确截取区域
3. 安装OCR进行识别测试
4. 使用完整版自动化

祝你学习愉快！🎓✨


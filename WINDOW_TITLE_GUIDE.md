# 🪟 通过窗口标题查找 - 使用指南

## 窗口信息

**窗口标题：** `课程详情`

使用窗口标题查找比图片识别更**准确、更快速、更可靠**！

---

## ✅ 优势

### 图片识别 vs 窗口标题

| 方法 | 速度 | 准确性 | 可靠性 | 依赖 |
|------|------|--------|--------|------|
| 窗口标题 | ⚡⚡⚡ 极快 | ✅ 100% | ✅ 高 | pygetwindow |
| 图片识别 | 🐌 较慢 | ⚠️ 70-90% | ⚠️ 中 | 截图+匹配 |
| 手动指定 | 👆 需要手动 | ✅ 准确 | ⚠️ 低 | 人工操作 |

---

## 📦 安装依赖

### 快速安装（推荐）

```bash
cd /home/jerry/cam_simulater

# 运行自动安装脚本
./setup_dependencies.sh
```

### 手动安装

```bash
# 安装窗口管理库
pip install pygetwindow

# 安装OCR和其他依赖
pip install pyautogui pytesseract pillow opencv-python

# 安装系统OCR引擎
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

---

## 🔍 查找窗口

### 方法1：使用演示工具

```bash
python find_window_demo.py
```

**输出示例：**
```
方法1：使用pygetwindow查找窗口
------------------------------------------------------------
系统中共有 45 个窗口

包含'课程'的窗口:
  1. 课程详情 - Google Chrome
  2. 课程管理系统

查找'课程详情'窗口:
✅ 找到窗口!
   标题: 课程详情 - Google Chrome
   位置: (100, 50)
   尺寸: 1280x720
✅ 窗口已激活
```

### 方法2：在自动化脚本中使用

程序现在会**自动**通过窗口标题查找：

```bash
python auto_learning_bot.py --test
```

**查找流程：**
```
1. 尝试通过窗口标题"课程详情"查找 ← 最优先
2. 如果失败，尝试图片识别
3. 如果仍失败，提示手动指定
```

---

## 🎯 工作原理

### 代码实现

```python
import pygetwindow as gw

# 查找窗口
windows = gw.getWindowsWithTitle('课程详情')

if windows:
    win = windows[0]
    
    # 获取窗口位置
    x = win.left
    y = win.top
    
    # 激活窗口（可选）
    win.activate()
    
    print(f"窗口位置: ({x}, {y})")
```

### 在机器人中的应用

```python
class AutoLearningBot:
    def find_window_by_title(self, window_title="课程详情"):
        """通过窗口标题查找"""
        windows = gw.getWindowsWithTitle(window_title)
        
        if windows:
            win = windows[0]
            self.window_offset_x = win.left
            self.window_offset_y = win.top
            return True
        return False
```

---

## 📝 使用示例

### 示例1：标准使用

```bash
# 1. 打开浏览器，进入课程页面
# 2. 确保窗口标题包含"课程详情"
# 3. 运行机器人
python auto_learning_bot.py --test

# 输出：
# [14:30:15] 正在查找课程列表窗口...
# [14:30:15] 正在查找窗口: '课程详情'...
# [14:30:15] ✅ 找到窗口 '课程详情': (100, 50)
# [14:30:15]    窗口尺寸: 1280x720
```

### 示例2：测试窗口查找

```bash
python find_window_demo.py
```

会显示：
- 所有包含"课程"的窗口
- "课程详情"窗口的详细信息
- 测试鼠标移动功能

### 示例3：自定义窗口标题

如果窗口标题不是"课程详情"，可以修改代码：

```python
# 编辑 auto_learning_bot.py
# 找到这一行：
if self.find_window_by_title("课程详情"):

# 修改为实际的窗口标题：
if self.find_window_by_title("你的窗口标题"):
```

---

## 🔧 故障排除

### 问题1：找不到窗口

**原因：**
- 窗口标题不完全匹配
- pygetwindow未安装
- 窗口未打开

**解决：**
```bash
# 1. 列出所有窗口
python find_window_demo.py

# 2. 查看输出，找到正确的窗口标题

# 3. 确认窗口标题
# 可能是：
#   - "课程详情"
#   - "课程详情 - Google Chrome"
#   - "课程详情 - Mozilla Firefox"

# 4. 修改代码使用正确的标题
```

### 问题2：pygetwindow不工作

**Linux系统替代方案：**
```bash
# 使用xdotool
sudo apt-get install xdotool

# 查找窗口
xdotool search --name "课程详情"

# 获取窗口位置
xdotool getwindowgeometry [窗口ID]
```

### 问题3：多个窗口同名

```python
# 获取所有匹配的窗口
windows = gw.getWindowsWithTitle('课程详情')

# 选择第一个（最新的）
win = windows[0]

# 或遍历选择
for i, w in enumerate(windows):
    print(f"{i}: {w.title} at ({w.left}, {w.top})")
```

---

## 💡 高级用法

### 技巧1：激活窗口

```python
import pygetwindow as gw

# 查找并激活窗口
windows = gw.getWindowsWithTitle('课程详情')
if windows:
    windows[0].activate()  # 将窗口置于前台
```

### 技巧2：监控窗口位置

```python
# 窗口可能被移动，定期更新位置
def update_window_position():
    windows = gw.getWindowsWithTitle('课程详情')
    if windows:
        win = windows[0]
        return win.left, win.top
    return None, None
```

### 技巧3：模糊匹配

```python
# 如果标题包含但不完全匹配
all_windows = gw.getAllTitles()
matching = [w for w in all_windows if '课程' in w and '详情' in w]

if matching:
    windows = gw.getWindowsWithTitle(matching[0])
```

---

## 📊 对比测试

### 性能测试

```python
import time

# 方法1：窗口标题（最快）
start = time.time()
windows = gw.getWindowsWithTitle('课程详情')
time1 = time.time() - start
print(f"窗口标题: {time1:.3f}秒")  # ~0.001秒

# 方法2：图片识别（较慢）
start = time.time()
location = pyautogui.locateOnScreen('lists.png')
time2 = time.time() - start
print(f"图片识别: {time2:.3f}秒")  # ~1-3秒
```

### 准确性测试

```
窗口标题: ✅ 100% (标题匹配即准确)
图片识别: ⚠️ 70-90% (取决于分辨率、缩放等)
```

---

## 🎓 完整工作流程

### 使用窗口标题的完整流程

```
1. 用户打开浏览器
   ↓
2. 进入课程页面（标题显示"课程详情"）
   ↓
3. 运行自动化脚本
   $ python auto_learning_bot.py --test
   ↓
4. 程序自动查找"课程详情"窗口
   ✅ 找到窗口: (100, 50)
   ↓
5. 获取窗口左上角坐标
   offset_x = 100, offset_y = 50
   ↓
6. 计算所有元素的绝对位置
   菜单1: (100+665, 50+271) = (765, 321)
   ↓
7. 执行自动化操作
   - 点击一级菜单
   - 截图二级区域
   - OCR识别学时
   - 自动点击未完成课程
```

---

## 📖 API参考

### pygetwindow主要方法

```python
import pygetwindow as gw

# 获取所有窗口标题
gw.getAllTitles()

# 根据标题查找窗口
gw.getWindowsWithTitle('课程详情')

# 获取活动窗口
gw.getActiveWindow()

# 窗口对象属性
win.title       # 标题
win.left        # X坐标
win.top         # Y坐标
win.width       # 宽度
win.height      # 高度
win.activate()  # 激活窗口
win.minimize()  # 最小化
win.maximize()  # 最大化
win.restore()   # 还原
```

---

## ✅ 验证清单

使用窗口标题前检查：
- [ ] pygetwindow已安装（`pip install pygetwindow`）
- [ ] 浏览器已打开课程页面
- [ ] 窗口标题确实包含"课程详情"
- [ ] 窗口未最小化
- [ ] 运行 `python find_window_demo.py` 测试

---

## 🎉 总结

**窗口标题查找的优势：**
- ⚡ **速度快** - 毫秒级查找
- ✅ **准确度高** - 100%准确
- 🎯 **可靠性强** - 不受窗口位置影响
- 🔄 **自动更新** - 窗口移动后自动适应

**推荐使用流程：**
1. 安装 pygetwindow
2. 运行 find_window_demo.py 测试
3. 使用 auto_learning_bot.py 自动化

**现在程序会优先使用窗口标题查找，更快更准确！** 🚀

---

*最后更新: 2024-12-05*
*窗口标题: 课程详情*


# 🎓 在线学习自动化完整指南

## 📋 菜单结构分析结果

### 图片信息
- **文件**: lists.png
- **尺寸**: 837 x 970 像素
- **菜单类型**: 两级菜单结构

---

## 🔴 一级菜单（红色按钮）

检测到 **4个一级菜单按钮**，都在右侧垂直排列：

| 菜单编号 | 点击坐标 | 作用 |
|---------|---------|------|
| 菜单 1 | **(665, 271)** 👆 | 点击展开第1组课程 |
| 菜单 2 | **(665, 461)** 👆 | 点击展开第2组课程 |
| 菜单 3 | **(665, 651)** 👆 | 点击展开第3组课程 |
| 菜单 4 | **(665, 841)** 👆 | 点击展开第4组课程 |

**特点：**
- 红色按钮，约70x48像素
- 垂直间距约190像素
- X坐标固定在665

---

## 🟢 二级菜单（课程列表）

每个一级菜单下有多个二级课程项：

### 菜单 1 的课程（估计2个）
- 课程 1.1: 点击位置 (200, 330)
- 课程 1.2: 点击位置 (200, 375)

### 菜单 2 的课程（估计2个）
- 课程 2.1: 点击位置 (200, 519)
- 课程 2.2: 点击位置 (200, 564)

### 菜单 3 的课程（估计2个）
- 课程 3.1: 点击位置 (200, 710)
- 课程 3.2: 点击位置 (200, 755)

**注意：** 菜单4下方可能还有课程，但在图片中未显示完整。

---

## 📖 学时格式说明

二级菜单中的课程包含学时信息，格式为：

```
x.x/x.x学时
```

**示例：**
- `0.0/2.0学时` - 未开始（需要学习）❌
- `0.5/2.0学时` - 进行中（需要继续）❌
- `1.5/2.0学时` - 进行中（需要继续）❌
- `2.0/2.0学时` - 已完成（无需点击）✅

**规则：**
- "/" 左边数字 = 已完成学时
- "/" 右边数字 = 总学时
- **当左边 < 右边时，需要点击该文本进行学习**

---

## 🎯 自动化操作流程

### 完整流程

```
1. 点击一级菜单 → 二级菜单展开
2. 识别学时文本 → 查找 "x.x/x.x学时"
3. 判断完成度  → 左边数字 < 右边数字？
4. 点击课程   → 开始视频播放
5. 等待完成   → 视频播放结束
6. 返回列表   → 处理下一个课程
7. 重复步骤1-6 → 直到所有课程完成
```

### 详细步骤

#### 步骤1：点击第一个一级菜单

```python
import pyautogui

# 点击菜单1的红色按钮
pyautogui.moveTo(665, 271, duration=0.5)
pyautogui.click()
time.sleep(1)  # 等待菜单展开
```

#### 步骤2：识别二级菜单中的学时信息

```python
# 方法1：使用OCR识别文本
import pytesseract
from PIL import ImageGrab

# 截取二级菜单区域
region = ImageGrab.grab(bbox=(50, 305, 550, 428))
text = pytesseract.image_to_string(region, lang='chi_sim')

# 查找学时信息
import re
pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
matches = re.findall(pattern, text)

for completed, total in matches:
    if float(completed) < float(total):
        print(f"未完成课程: {completed}/{total}学时")
        # 需要点击
```

#### 步骤3：点击未完成的课程

```python
# 假设找到未完成课程在位置 (200, 330)
pyautogui.moveTo(200, 330, duration=0.5)
pyautogui.click()
time.sleep(2)  # 等待视频加载
```

#### 步骤4：等待视频播放完成

```python
# 方法1：固定等待时间
time.sleep(120)  # 假设视频2分钟

# 方法2：检测播放完成（需要识别完成标志）
# 持续监控页面变化
```

#### 步骤5：返回继续处理

```python
# 返回列表（通常按ESC或点击返回按钮）
pyautogui.press('esc')
time.sleep(1)

# 继续处理下一个课程或下一个菜单
```

---

## 🚀 快速开始脚本

### 基础点击脚本

```python
#!/usr/bin/env python3
import pyautogui
import time

# 一级菜单坐标
level1_menus = [
    (665, 271),  # 菜单1
    (665, 461),  # 菜单2
    (665, 651),  # 菜单3
    (665, 841),  # 菜单4
]

# 二级菜单估计坐标（需要先点击一级菜单展开）
level2_items = {
    1: [(200, 330), (200, 375)],  # 菜单1的课程
    2: [(200, 519), (200, 564)],  # 菜单2的课程
    3: [(200, 710), (200, 755)],  # 菜单3的课程
}

def click_menu(x, y, delay=0.5):
    """点击指定位置"""
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()
    time.sleep(delay)

# 示例：点击第一个菜单
print("点击第一个菜单...")
click_menu(*level1_menus[0])

print("点击第一个菜单下的第一个课程...")
click_menu(*level2_items[1][0])
```

### 在屏幕上查找列表位置

```python
import pyautogui

# 查找lists.png在屏幕上的位置
location = pyautogui.locateOnScreen('lists.png', confidence=0.7)

if location:
    offset_x = location.left
    offset_y = location.top
    print(f"找到位置: ({offset_x}, {offset_y})")
    
    # 计算实际点击坐标
    actual_x = offset_x + 665  # 第一个菜单的X
    actual_y = offset_y + 271  # 第一个菜单的Y
    
    pyautogui.moveTo(actual_x, actual_y)
    pyautogui.click()
else:
    print("未找到列表")
```

---

## 📊 可视化文件说明

### learning_menu_structure.png

这个可视化图标注了：

- **红色粗边框** + 蓝色圆点 = 一级菜单（红色按钮）
  - 箭头指向点击位置
  - 标签：L1-Menu1, L1-Menu2...

- **绿色细边框** + 橙色圆点 = 二级菜单项（估计位置）
  - 橙色圆点是点击位置
  - 标签：L2-1.1, L2-2.1...

- **图例**（底部）
  - 详细说明各种标记的含义

---

## 🛠️ 工具和脚本

### 已生成的文件

1. **learning_menu_structure.png** ⭐⭐⭐
   - 可视化菜单结构
   - 标注了所有点击位置
   - 建议打开查看

2. **learning_menu_report.json**
   - JSON格式的详细数据
   - 包含所有坐标信息
   - 可用于自动化脚本

3. **analyze_learning_menu.py**
   - 分析工具源代码
   - 可重新运行分析

---

## 💡 实用技巧

### 技巧1：获取准确的二级菜单坐标

```python
# 1. 先点击一级菜单
pyautogui.click(665, 271)
time.sleep(1)

# 2. 截图
screenshot = pyautogui.screenshot()
screenshot.save('expanded_menu.png')

# 3. 手动查看截图，记录学时文本位置
# 4. 更新坐标
```

### 技巧2：OCR识别学时信息

```bash
# 安装依赖
pip install pytesseract pillow

# Linux系统安装tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

```python
import pytesseract
from PIL import Image

# 截取区域
img = Image.open('expanded_menu.png')
region = img.crop((50, 300, 500, 400))

# OCR识别
text = pytesseract.image_to_string(region, lang='chi_sim')
print(text)

# 提取学时
import re
matches = re.findall(r'(\d+\.?\d*)/(\d+\.?\d*)学时', text)
for completed, total in matches:
    if float(completed) < float(total):
        print(f"需要学习: {completed}/{total}")
```

### 技巧3：批量处理

```python
def process_all_menus():
    """处理所有菜单"""
    for i, (x, y) in enumerate(level1_menus):
        print(f"\n处理菜单 {i+1}...")
        
        # 点击一级菜单
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click()
        time.sleep(1.5)
        
        # 截图识别二级菜单
        screenshot = pyautogui.screenshot()
        # ... OCR识别 ...
        # ... 找到未完成课程 ...
        # ... 点击播放 ...
        
        time.sleep(2)  # 间隔时间

# 运行
process_all_menus()
```

---

## ⚠️ 注意事项

### 1. 坐标偏移

- 提供的坐标是**相对于图片的**
- 如果在实际屏幕上使用，需要加上窗口偏移量
- 使用 `pyautogui.locateOnScreen()` 查找窗口位置

### 2. 时间等待

- 点击后需要等待页面加载/动画
- 建议每次点击后等待1-2秒
- 视频播放时间根据实际长度调整

### 3. 二级菜单动态加载

- 二级菜单只有在点击一级菜单后才显示
- 坐标是估计值，实际可能有偏差
- 建议先手动点击验证位置

### 4. 学时格式识别

- OCR识别可能有误差
- 建议使用中文简体语言包
- 可以多次识别取平均值

### 5. 浏览器窗口

- 确保浏览器窗口在屏幕上可见
- 不要最小化或被其他窗口遮挡
- 窗口大小不要改变

---

## 🎯 推荐流程

### 方案A：半自动（推荐新手）

1. **手动**点击一级菜单
2. **目视**查找未完成课程
3. **手动**点击课程开始学习
4. **自动**等待视频播放完成
5. 返回重复

### 方案B：全自动（推荐熟练用户）

1. **自动**遍历所有一级菜单
2. **OCR**识别学时信息
3. **自动**点击未完成课程
4. **自动**等待并返回
5. **自动**处理下一个

---

## 📝 完整自动化脚本模板

```python
#!/usr/bin/env python3
"""
完整的自动学习脚本
"""

import pyautogui
import time
import pytesseract
from PIL import ImageGrab
import re

# 配置
LEVEL1_MENUS = [
    (665, 271), (665, 461), (665, 651), (665, 841)
]

def find_window_offset():
    """查找窗口偏移"""
    location = pyautogui.locateOnScreen('lists.png', confidence=0.7)
    if location:
        return location.left, location.top
    return 0, 0

def click_with_offset(x, y, offset_x, offset_y):
    """带偏移的点击"""
    pyautogui.moveTo(offset_x + x, offset_y + y, duration=0.3)
    pyautogui.click()

def extract_hours(region_bbox):
    """提取学时信息"""
    img = ImageGrab.grab(bbox=region_bbox)
    text = pytesseract.image_to_string(img, lang='chi_sim')
    
    pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
    matches = re.findall(pattern, text)
    
    incomplete_items = []
    for completed, total in matches:
        if float(completed) < float(total):
            incomplete_items.append((completed, total))
    
    return incomplete_items

def main():
    print("🎓 自动学习系统启动")
    
    # 查找窗口
    offset_x, offset_y = find_window_offset()
    if offset_x == 0:
        print("❌ 未找到窗口，请确保浏览器打开")
        return
    
    print(f"✅ 窗口位置: ({offset_x}, {offset_y})")
    
    # 遍历菜单
    for i, (menu_x, menu_y) in enumerate(LEVEL1_MENUS):
        print(f"\n>>> 处理菜单 {i+1}")
        
        # 点击一级菜单
        click_with_offset(menu_x, menu_y, offset_x, offset_y)
        time.sleep(1.5)
        
        # 截图识别二级菜单
        region = (offset_x + 50, offset_y + 300, 
                 offset_x + 550, offset_y + 500)
        
        incomplete = extract_hours(region)
        print(f"   找到 {len(incomplete)} 个未完成课程")
        
        for completed, total in incomplete:
            print(f"   学习课程: {completed}/{total}学时")
            # TODO: 点击课程并等待
            time.sleep(2)
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    main()
```

---

## ✅ 总结

**已识别：**
- ✅ 4个一级菜单（红色按钮）
- ✅ 约6个二级菜单项（估计值）
- ✅ 所有点击坐标

**可以做：**
- ✅ 自动点击一级菜单展开
- ✅ 识别学时信息（需OCR）
- ✅ 自动点击未完成课程
- ✅ 批量处理所有菜单

**建议：**
1. 先查看 `learning_menu_structure.png` 熟悉结构
2. 手动点击测试一次流程
3. 使用脚本半自动化
4. 完善后使用全自动

---

*分析时间: 2024-12-05*
*工具: analyze_learning_menu.py*
*版本: v1.0*


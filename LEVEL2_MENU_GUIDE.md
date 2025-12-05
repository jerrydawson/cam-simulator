# 📋 二级菜单识别指南

## 什么是二级菜单？

**二级菜单** = 点击红色按钮（一级菜单）后展开的课程列表

包含：
- 课程名称
- **学时信息**（"x.x/x.x学时"）← 重点识别对象
- 课程状态
- 其他信息

---

## 📊 二级菜单特征分析

### 基于 lists_full.png 的分析结果

#### **一级菜单（触发器）**
- **数量**: 3个红色按钮
- **位置**: Y=742, Y=1801, Y=1991
- **作用**: 点击后展开对应的二级菜单

#### **二级菜单区域**

| 一级按钮 | Y范围 | 高度 | 估计课程数 |
|---------|-------|------|-----------|
| 按钮1 | 771 ~ 1772 | 1001px | 约18个 |
| 按钮2 | 1830 ~ 1963 | 133px | 约2个 |
| **总计** | - | - | **约20个** |

#### **课程项特征**
- **平均高度**: 约55px
- **间距**: 约5-10px
- **文本颜色**: 黑色/深灰 (2.7%), 蓝色 (21.0%)

---

## 🎯 二级菜单识别策略

### 策略1：基于一级按钮位置推算

```python
# 1. 检测一级按钮
level1_button = detect_red_button()  # Y=742

# 2. 计算二级菜单区域
level2_start = level1_button['y'] + level1_button['height'] + 5
level2_end = next_button['y'] - 5  # 或图片底部

# 3. 估计课程项位置
item_height = 55  # 每个课程约55px
num_items = (level2_end - level2_start) / item_height

# 4. 计算每个课程的Y坐标
for i in range(num_items):
    course_y = level2_start + 30 + i * 55
    # 在此位置搜索学时文本
```

### 策略2：展开后实时检测

```python
# 1. 点击一级按钮
click(level1_button_x, level1_button_y)

# 2. 等待展开
time.sleep(0.8)

# 3. 截图二级菜单区域
screenshot = capture_region(
    x=0,
    y=level2_start,
    width=screen_width,
    height=level2_height
)

# 4. OCR识别学时信息
hours_data = ocr_extract_hours(screenshot)

# 5. 定位需要点击的课程
for course in hours_data:
    if course['completed'] < course['total']:
        click(course['x'], course['y'])
```

---

## 🔍 学时文本特征

### 位置特征

**水平位置（X坐标）**
- 通常在：150-250px 范围
- 建议搜索策略：先在左侧 1/3 区域查找

**垂直位置（Y坐标）**
- 相对于一级按钮：下方 30px 开始
- 每个课程间隔：约55px
- 公式：`Y = 一级按钮Y + 按钮高度 + 30 + (课程索引 * 55)`

### 文本特征

**格式**
```
x.x/x.x学时
```

**示例**
- `0.0/2.0学时` ← 未开始
- `1.5/2.0学时` ← 进行中
- `2.0/2.0学时` ← 已完成

**颜色**
- 黑色或深灰色（常规状态）
- 蓝色（可能是链接样式）

**尺寸**
- 高度：约15-25px（基于平均19.5px）
- 宽度：约80-120px

---

## 💡 识别流程

### 完整识别流程

```
第1步：检测一级菜单
   ↓
找到红色按钮位置 (Y=742)
   ↓
第2步：点击展开
   ↓
click(665, 742)
wait(0.8秒)
   ↓
第3步：计算二级区域
   ↓
region_start = 771
region_end = 1772
region_height = 1001px
   ↓
第4步：估计课程位置
   ↓
course_1_y = 771 + 30 = 801
course_2_y = 771 + 30 + 55 = 856
course_3_y = 771 + 30 + 110 = 911
...
   ↓
第5步：截图并OCR
   ↓
在每个course_y位置附近搜索
识别 "x.x/x.x学时" 模式
   ↓
第6步：判断并点击
   ↓
if 左边 < 右边:
    click(x, y)
```

---

## 🚀 实现代码

### 方法1：基于位置估算（无OCR）

```python
class Level2MenuHandler:
    def process_level1_button(self, button_y):
        """处理一个一级菜单"""
        # 1. 点击展开
        click(665, button_y)
        time.sleep(0.8)
        
        # 2. 计算二级区域
        region_start = button_y + 50 + 20
        
        # 3. 估计课程位置（假设有10个课程）
        for i in range(10):
            course_y = region_start + 30 + i * 55
            
            # 4. 点击学时文本位置
            # 假设学时文本在X=200处
            click(200, course_y)
            time.sleep(0.5)
```

### 方法2：基于OCR识别（推荐）

```python
def process_with_ocr(level1_button_y):
    """使用OCR识别二级菜单"""
    # 1. 点击展开
    click(665, level1_button_y)
    time.sleep(0.8)
    
    # 2. 计算并截图二级区域
    region_start = level1_button_y + 70
    region_height = 600  # 估计高度
    
    screenshot = capture_region(
        x=0, y=region_start,
        width=866, height=region_height
    )
    
    # 3. OCR识别
    text = pytesseract.image_to_string(screenshot, lang='chi_sim')
    
    # 4. 提取学时信息
    pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
    matches = re.findall(pattern, text)
    
    # 5. 处理每个课程
    for i, (completed, total) in enumerate(matches):
        if float(completed) < float(total):
            # 计算点击位置
            course_y = region_start + 30 + i * 55
            click(200, course_y)
            time.sleep(0.5)
```

### 方法3：精确OCR定位（最准确）

```python
from pytesseract import Output

def precise_ocr_detection(region_image, region_offset_y):
    """精确OCR识别并获取坐标"""
    # OCR with bounding boxes
    data = pytesseract.image_to_data(
        region_image, 
        lang='chi_sim',
        output_type=Output.DICT
    )
    
    hours_items = []
    
    # 遍历所有识别的文本
    for i, text in enumerate(data['text']):
        if not text.strip():
            continue
        
        # 匹配学时模式
        pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
        match = re.search(pattern, text)
        
        if match:
            completed = float(match.group(1))
            total = float(match.group(2))
            
            # 获取精确位置
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            conf = data['conf'][i]
            
            hours_items.append({
                'completed': completed,
                'total': total,
                'x': x,
                'y': region_offset_y + y,  # 加上偏移
                'width': w,
                'height': h,
                'click_x': x + w // 2,
                'click_y': region_offset_y + y + h // 2,
                'confidence': int(conf),
                'incomplete': completed < total
            })
    
    return hours_items
```

---

## 📐 坐标计算

### 二级菜单区域坐标

```python
# 一级按钮信息
button_1 = {'y': 742, 'height': 50}
button_2 = {'y': 1801, 'height': 50}

# 二级菜单1的区域
level2_menu_1 = {
    'y_start': 742 + 50 + 5,    # = 797
    'y_end': 1801 - 5,          # = 1796
    'height': 1796 - 797,       # = 999px
}

# 二级菜单2的区域
level2_menu_2 = {
    'y_start': 1801 + 50 + 5,   # = 1856
    'y_end': 2056 - 100,        # = 1956（底部留空）
    'height': 1956 - 1856,      # = 100px
}
```

### 课程项坐标

```python
def get_course_coordinates(menu_y_start, course_index):
    """计算第N个课程的坐标"""
    base_y = menu_y_start + 30  # 第一个课程位置
    course_y = base_y + course_index * 55
    
    return {
        'x': 200,  # 学时文本X位置
        'y': course_y,
        'click_point': (200, course_y)
    }

# 示例：一级按钮1的第3个课程
coords = get_course_coordinates(797, 2)  # 索引从0开始
# 结果：{'x': 200, 'y': 907, 'click_point': (200, 907)}
```

---

## 🎨 可视化说明

### 查看生成的可视化图

```bash
xdg-open level2_menu_analyzed.png
```

**图中标注：**
- 🔴 红色框：一级菜单按钮
- 🟦 蓝色/绿色框：二级菜单区域
- 🟠 橙色圆点：学时文本位置
- 横线：课程项分隔

---

## ⚙️ 优化参数

### 可调参数

```python
# 等待时间
EXPAND_WAIT_TIME = 0.8  # 点击后等待二级菜单展开
CLICK_WAIT_TIME = 0.5   # 点击课程后等待

# 布局参数
COURSE_HEIGHT = 55      # 每个课程项高度
FIRST_COURSE_OFFSET = 30  # 第一个课程相对于区域顶部的偏移
HOURS_TEXT_X = 200      # 学时文本X坐标

# 区域边距
REGION_TOP_MARGIN = 5   # 二级区域顶部边距
REGION_BOTTOM_MARGIN = 5  # 二级区域底部边距
```

### 调优建议

**如果课程位置不准：**
```python
# 调整课程高度
COURSE_HEIGHT = 50  # 或 60, 55

# 调整起始偏移
FIRST_COURSE_OFFSET = 25  # 或 35, 40
```

**如果学时文本找不到：**
```python
# 扩大搜索范围
for x in range(150, 300, 10):  # 在150-300范围搜索
    for y in [course_y - 5, course_y, course_y + 5]:
        check_hours_text(x, y)
```

---

## 📊 实际数据

### 基于 lists_full.png 的测量

| 参数 | 测量值 | 备注 |
|------|--------|------|
| **一级按钮数量** | 3个 | - |
| **二级区域1** | 797-1796 (999px) | 约18个课程 |
| **二级区域2** | 1856-1956 (100px) | 约2个课程 |
| **课程项高度** | 55px | 平均值 |
| **学时文本X** | 150-250 | 估计范围 |
| **文本高度** | 19.5px | 平均值 |

---

## ✅ 使用检查清单

处理二级菜单前：
- [ ] 已检测到一级按钮位置
- [ ] 已计算二级菜单区域
- [ ] 已设置等待时间
- [ ] OCR已安装配置（如使用）

处理过程中：
- [ ] 点击一级按钮
- [ ] 等待展开（0.8秒）
- [ ] 截图二级区域
- [ ] 识别学时信息
- [ ] 判断是否未完成
- [ ] 点击未完成课程

---

## 🎯 完整示例

```python
#!/usr/bin/env python3
"""完整的二级菜单处理示例"""

import cv2
import pytesseract
import pyautogui
import time
import re

def process_level2_menu(level1_button_y):
    """处理二级菜单"""
    
    # 1. 点击一级按钮展开
    print(f"点击一级按钮: Y={level1_button_y}")
    pyautogui.moveTo(665, level1_button_y, duration=0.3)
    pyautogui.click()
    time.sleep(0.8)  # 等待展开
    
    # 2. 计算二级区域
    region_start = level1_button_y + 70
    region_height = 600
    
    # 3. 截图
    print("截图二级菜单区域...")
    screenshot = pyautogui.screenshot(
        region=(0, region_start, 866, region_height)
    )
    
    # 4. OCR识别
    print("OCR识别学时信息...")
    img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(img_cv, lang='chi_sim')
    
    # 5. 提取学时
    pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
    matches = re.findall(pattern, text)
    
    print(f"找到 {len(matches)} 个课程")
    
    # 6. 处理每个课程
    incomplete_count = 0
    for i, (completed, total) in enumerate(matches):
        c = float(completed)
        t = float(total)
        
        if c < t:
            print(f"课程 {i+1}: {c}/{t}学时 - 未完成")
            
            # 计算点击位置
            course_y = region_start + 30 + i * 55
            
            # 点击
            pyautogui.moveTo(200, course_y, duration=0.3)
            pyautogui.click()
            time.sleep(0.5)
            
            incomplete_count += 1
        else:
            print(f"课程 {i+1}: {c}/{t}学时 - 已完成")
    
    print(f"处理了 {incomplete_count} 个未完成课程")
    return incomplete_count

# 使用
if __name__ == '__main__':
    # 处理第一个一级菜单
    process_level2_menu(742)
```

---

## 🎉 总结

**二级菜单识别关键点：**

1. ✅ **位置估算** - 基于一级按钮位置 + 偏移
2. ✅ **等待时间** - 0.8秒等待展开
3. ✅ **区域计算** - Y范围：按钮下方到下一按钮
4. ✅ **课程间距** - 约55px/个
5. ✅ **学时位置** - X约150-250，Y按课程索引计算
6. ✅ **OCR识别** - 优先使用，准确率高

**生成的文件：**
- `level2_menu_analyzed.png` - 可视化标注
- `level2_menu_report.json` - 详细数据

**立即查看：**
```bash
xdg-open level2_menu_analyzed.png
cat level2_menu_report.json
```

---

*基于 lists_full.png (866x2056) 的二级菜单分析*  
*更新时间: 2024-12-05*


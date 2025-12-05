#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动学习点击器
自动识别课程学时进度，点击未完成的课程
"""

import cv2
import numpy as np
import pyautogui
import time
import re
from PIL import Image

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("⚠️  pytesseract未安装，将使用备用方法")


class LearningAutoClicker:
    def __init__(self, image_path='lists.png'):
        self.image_path = image_path
        self.image = None
        self.level1_buttons = []  # 一级菜单按钮（红色）
        self.level2_items = []     # 二级菜单项
        
    def load_image(self):
        """加载图片"""
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"无法加载图片: {self.image_path}")
        print(f"✅ 图片已加载: {self.image.shape[1]}x{self.image.shape[0]}")
    
    def detect_level1_menus(self):
        """检测一级菜单（红色按钮）"""
        print("\n🔍 检测一级菜单（红色按钮）...")
        
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 红色范围
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # 最小面积
                x, y, w, h = cv2.boundingRect(contour)
                if w > 40 and h > 30:  # 最小尺寸
                    buttons.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'level': 1
                    })
        
        # 按Y坐标排序
        buttons.sort(key=lambda b: b['y'])
        
        # 去重（相近的按钮合并）
        unique_buttons = []
        for btn in buttons:
            is_duplicate = False
            for existing in unique_buttons:
                if abs(btn['center_y'] - existing['center_y']) < 50:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_buttons.append(btn)
        
        self.level1_buttons = unique_buttons
        print(f"   找到 {len(self.level1_buttons)} 个一级菜单按钮")
        
        for i, btn in enumerate(self.level1_buttons):
            print(f"   菜单 {i+1}: 位置 ({btn['center_x']}, {btn['center_y']})")
        
        return self.level1_buttons
    
    def extract_text_regions(self):
        """提取所有文本区域"""
        print("\n📝 提取文本区域...")
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # 使用自适应阈值
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 文本区域特征：宽度较大，高度适中
            if 100 < w < 600 and 15 < h < 50:
                text_regions.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                })
        
        print(f"   找到 {len(text_regions)} 个文本区域候选")
        return text_regions
    
    def ocr_learning_hours(self, region):
        """OCR识别学时信息"""
        if not HAS_OCR:
            return None
        
        try:
            # 提取区域
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            roi = self.image[y:y+h, x:x+w]
            
            # 预处理
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # 增强对比度
            gray = cv2.equalizeHist(gray)
            
            # OCR
            text = pytesseract.image_to_string(gray, lang='chi_sim+eng', 
                                              config='--psm 7')
            text = text.strip()
            
            # 匹配学时格式：x.x/x.x学时
            pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
            match = re.search(pattern, text)
            
            if match:
                completed = float(match.group(1))
                total = float(match.group(2))
                return {
                    'text': text,
                    'completed': completed,
                    'total': total,
                    'is_incomplete': completed < total,
                    'region': region
                }
        except Exception as e:
            pass
        
        return None
    
    def detect_learning_hours_pattern(self):
        """检测学时模式（不使用OCR的备用方法）"""
        print("\n🔍 检测学时文本（模式匹配）...")
        
        # 基于位置和颜色特征检测
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # 查找包含"/"字符的区域
        # 这需要模板匹配或特定的特征检测
        
        # 简化版：基于位置推测
        # 二级菜单通常在一级菜单的下方，左侧对齐
        learning_items = []
        
        # 对每个一级菜单，查找其下方的可能二级菜单
        for i, btn in enumerate(self.level1_buttons):
            # 二级菜单区域：一级按钮下方到下一个一级按钮之间
            y_start = btn['y'] + btn['height']
            if i + 1 < len(self.level1_buttons):
                y_end = self.level1_buttons[i + 1]['y']
            else:
                y_end = self.image.shape[0]
            
            # 在这个区域内查找文本
            region_height = y_end - y_start
            if region_height > 50:  # 有足够空间
                # 假设二级菜单项的垂直间距约为40-50px
                num_items = max(1, (region_height - 50) // 45)
                
                for j in range(int(num_items)):
                    y_pos = y_start + 30 + j * 45
                    if y_pos < y_end - 20:
                        learning_items.append({
                            'level1_index': i,
                            'level2_index': j,
                            'x': 50,  # 左侧位置
                            'y': y_pos,
                            'center_x': 300,  # 大致中心
                            'center_y': y_pos,
                            'parent_button': btn
                        })
        
        print(f"   检测到约 {len(learning_items)} 个可能的二级菜单项")
        return learning_items
    
    def analyze_and_visualize(self):
        """分析并可视化"""
        print("\n" + "=" * 70)
        print("📋 课程菜单结构分析")
        print("=" * 70)
        
        self.load_image()
        
        # 检测一级菜单
        level1_menus = self.detect_level1_menus()
        
        # 尝试OCR识别学时
        if HAS_OCR:
            text_regions = self.extract_text_regions()
            learning_hours = []
            
            print("\n📖 OCR识别学时信息...")
            for region in text_regions:
                result = self.ocr_learning_hours(region)
                if result:
                    learning_hours.append(result)
            
            if learning_hours:
                print(f"\n✅ 识别到 {len(learning_hours)} 个学时信息:")
                for i, item in enumerate(learning_hours):
                    status = "❌ 未完成" if item['is_incomplete'] else "✅ 已完成"
                    print(f"   {i+1}. {item['text']} - {status}")
                    print(f"      位置: ({item['region']['center_x']}, {item['region']['center_y']})")
        else:
            # 备用方法
            learning_hours = self.detect_learning_hours_pattern()
        
        # 生成可视化
        self.create_visualization(level1_menus, learning_hours if HAS_OCR else [])
        
        return level1_menus, learning_hours if HAS_OCR else []
    
    def create_visualization(self, level1_menus, learning_hours):
        """创建可视化图"""
        result = self.image.copy()
        
        # 绘制一级菜单
        for i, menu in enumerate(level1_menus):
            cv2.rectangle(result, 
                         (menu['x'], menu['y']),
                         (menu['x'] + menu['width'], menu['y'] + menu['height']),
                         (0, 0, 255), 3)
            cv2.circle(result, (menu['center_x'], menu['center_y']), 8, (255, 0, 0), -1)
            cv2.putText(result, f"L1-{i+1}", 
                       (menu['x'] - 50, menu['center_y']),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 绘制学时信息
        if HAS_OCR and learning_hours:
            for item in learning_hours:
                region = item['region']
                color = (0, 255, 0) if not item['is_incomplete'] else (0, 165, 255)  # 绿色/橙色
                
                cv2.rectangle(result,
                             (region['x'], region['y']),
                             (region['x'] + region['width'], region['y'] + region['height']),
                             color, 2)
                
                if item['is_incomplete']:
                    # 标记需要点击
                    cv2.circle(result, (region['center_x'], region['center_y']), 10, (0, 0, 255), -1)
                    cv2.putText(result, "CLICK!", 
                               (region['x'], region['y'] - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 添加图例
        legend_y = 30
        cv2.putText(result, "Red Box: Level 1 Menu | Orange: Incomplete | Green: Complete",
                   (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        output_path = 'learning_menu_analyzed.png'
        cv2.imwrite(output_path, result)
        print(f"\n✅ 可视化结果: {output_path}")


def generate_click_script(level1_menus):
    """生成点击脚本"""
    script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
自动学习点击脚本
按照菜单层级自动点击未完成的课程
\"\"\"

import pyautogui
import time

# 一级菜单按钮坐标（红色按钮）
level1_buttons = [
"""
    
    for i, menu in enumerate(level1_menus):
        script += f"    {{'index': {i+1}, 'x': {menu['center_x']}, 'y': {menu['center_y']}}},  # 菜单{i+1}\n"
    
    script += """]

def click_level1_menu(menu_index, offset_x=0, offset_y=0):
    \"\"\"点击一级菜单\"\"\"
    if 0 <= menu_index < len(level1_buttons):
        btn = level1_buttons[menu_index]
        x = offset_x + btn['x']
        y = offset_y + btn['y']
        
        print(f"点击一级菜单 {btn['index']}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click()
        time.sleep(0.5)  # 等待菜单展开
    else:
        print(f"错误: 菜单索引超出范围")

def find_image_on_screen(image_path='lists.png'):
    \"\"\"在屏幕上查找图片位置\"\"\"
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=0.7)
        if location:
            return location.left, location.top
    except Exception as e:
        print(f"查找图片失败: {e}")
    return None, None

def auto_learn():
    \"\"\"自动学习流程\"\"\"
    print("=" * 60)
    print("自动学习点击器")
    print("=" * 60)
    
    # 1. 查找图片位置
    print("\\n步骤1: 在屏幕上查找课程列表...")
    offset_x, offset_y = find_image_on_screen()
    
    if offset_x is None:
        print("❌ 未找到课程列表，请确保浏览器打开并显示课程页面")
        return
    
    print(f"✅ 找到位置: ({offset_x}, {offset_y})")
    
    # 2. 遍历一级菜单
    print(f"\\n步骤2: 开始遍历 {len(level1_buttons)} 个一级菜单...")
    
    for i in range(len(level1_buttons)):
        print(f"\\n>>> 处理菜单 {i+1}...")
        
        # 点击一级菜单展开
        click_level1_menu(i, offset_x, offset_y)
        
        # 这里需要添加二级菜单的识别和点击逻辑
        # 由于二级菜单动态生成，需要实时截图分析
        
        print(f"    等待2秒观察二级菜单...")
        time.sleep(2)
        
        # TODO: 识别二级菜单中的 "x.x/x.x学时" 文本
        # TODO: 比较数字，如果不相等则点击
        
    print("\\n✅ 处理完成！")

def manual_click_menu(menu_index):
    \"\"\"手动点击指定菜单\"\"\"
    print(f"\\n准备点击菜单 {menu_index}...")
    print("请确保课程列表在屏幕上可见")
    print("3秒后开始...")
    time.sleep(3)
    
    offset_x, offset_y = find_image_on_screen()
    if offset_x:
        click_level1_menu(menu_index - 1, offset_x, offset_y)
    else:
        print("未找到课程列表")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 手动点击指定菜单
        menu_num = int(sys.argv[1])
        manual_click_menu(menu_num)
    else:
        # 自动学习模式
        print("用法:")
        print("  自动模式: python learning_click_script.py")
        print("  手动模式: python learning_click_script.py <菜单编号>")
        print("\\n示例:")
        print("  python learning_click_script.py 1  # 点击第1个菜单")
        print()
        
        choice = input("启动自动学习? (y/n): ")
        if choice.lower() == 'y':
            auto_learn()
"""
    
    with open('learning_click_script.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("✅ 点击脚本已生成: learning_click_script.py")


def main():
    print("=" * 70)
    print("🎓 在线学习自动点击器")
    print("=" * 70)
    print("\n功能说明:")
    print("  1. 识别一级菜单（红色按钮）")
    print("  2. 识别二级菜单中的学时信息 (x.x/x.x学时)")
    print("  3. 自动点击未完成的课程 (左右数字不相等)")
    print()
    
    if not HAS_OCR:
        print("⚠️  提示: 未安装OCR库，建议安装以获得更好的识别效果")
        print("   安装命令: pip install pytesseract")
        print("   还需要安装tesseract-ocr系统包")
        print()
    
    clicker = LearningAutoClicker('lists.png')
    level1_menus, learning_hours = clicker.analyze_and_visualize()
    
    # 生成脚本
    generate_click_script(level1_menus)
    
    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)
    print("\n生成的文件:")
    print("  1. learning_menu_analyzed.png    - 可视化菜单结构")
    print("  2. learning_click_script.py      - 自动点击脚本")
    print("\n使用方法:")
    print("  查看可视化: xdg-open learning_menu_analyzed.png")
    print("  运行脚本: python learning_click_script.py")


if __name__ == '__main__':
    main()


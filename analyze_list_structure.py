#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片列表结构分析工具
分析图片中的列表、按钮、菜单等UI元素
"""

import cv2
import numpy as np
from PIL import Image
import json


def analyze_list_structure(image_path):
    """分析列表结构"""
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return None
    
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    print("=" * 70)
    print("📋 列表结构详细分析")
    print("=" * 70)
    print(f"图片: {image_path}")
    print(f"尺寸: {width}x{height} 像素")
    print()
    
    # 1. 检测水平分隔线（列表项之间的分隔）
    print("🔍 检测水平分隔线...")
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 2, 1))
    horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, horizontal_kernel)
    horizontal_edges = cv2.Canny(horizontal_lines, 50, 150)
    
    # 找到水平线
    lines = cv2.HoughLinesP(horizontal_edges, 1, np.pi/180, threshold=100, minLineLength=width//3, maxLineGap=20)
    
    horizontal_y_positions = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y2 - y1) < 5:  # 几乎水平的线
                horizontal_y_positions.append(y1)
    
    horizontal_y_positions = sorted(set(horizontal_y_positions))
    print(f"   找到 {len(horizontal_y_positions)} 条水平分隔线")
    
    # 2. 检测列表项（根据分隔线分割）
    list_items = []
    if horizontal_y_positions:
        for i in range(len(horizontal_y_positions) - 1):
            y1 = horizontal_y_positions[i]
            y2 = horizontal_y_positions[i + 1]
            if y2 - y1 > 30:  # 最小项目高度
                list_items.append({
                    'index': len(list_items) + 1,
                    'y_start': y1,
                    'y_end': y2,
                    'height': y2 - y1,
                    'center_y': (y1 + y2) // 2
                })
    
    # 3. 使用颜色检测按钮/交互元素
    print("\n🎨 检测彩色元素（按钮/菜单）...")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 检测不同颜色的区域
    color_ranges = {
        '蓝色': ([100, 50, 50], [130, 255, 255]),
        '绿色': ([40, 50, 50], [80, 255, 255]),
        '红色': ([0, 50, 50], [10, 255, 255]),
        '橙色': ([10, 50, 50], [25, 255, 255]),
    }
    
    buttons = []
    for color_name, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:  # 最小面积
                x, y, w, h = cv2.boundingRect(contour)
                if w > 30 and h > 20:  # 最小尺寸
                    buttons.append({
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'color': color_name,
                        'area': area
                    })
    
    # 去重（按位置）
    buttons_unique = []
    for btn in buttons:
        is_duplicate = False
        for existing in buttons_unique:
            if abs(btn['center_x'] - existing['center_x']) < 20 and \
               abs(btn['center_y'] - existing['center_y']) < 20:
                is_duplicate = True
                break
        if not is_duplicate:
            buttons_unique.append(btn)
    
    buttons = sorted(buttons_unique, key=lambda b: b['y'])
    print(f"   找到 {len(buttons)} 个彩色交互元素")
    
    # 4. 检测文本区域（使用MSER）
    print("\n📝 检测文本区域...")
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    
    text_regions = []
    for region in regions:
        if len(region) > 10:
            x, y, w, h = cv2.boundingRect(region)
            if 15 < h < 50 and w > 30:  # 文本高度范围
                text_regions.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                })
    
    print(f"   找到 {len(text_regions)} 个可能的文本区域")
    
    # 5. 打印详细结构
    print("\n" + "=" * 70)
    print("📊 结构分析结果")
    print("=" * 70)
    
    if list_items:
        print(f"\n✅ 检测到 {len(list_items)} 个列表项:")
        print("-" * 70)
        for item in list_items:
            print(f"  项目 {item['index']}:")
            print(f"    Y范围: {item['y_start']} ~ {item['y_end']}")
            print(f"    高度: {item['height']}px")
            print(f"    中心点: (宽度中心, {item['center_y']})")
            
            # 找到这个列表项中的按钮
            item_buttons = [b for b in buttons if item['y_start'] < b['center_y'] < item['y_end']]
            if item_buttons:
                print(f"    包含 {len(item_buttons)} 个按钮:")
                for btn in item_buttons:
                    print(f"      - {btn['color']}按钮 at ({btn['center_x']}, {btn['center_y']})")
            print()
    
    if buttons:
        print(f"\n✅ 检测到 {len(buttons)} 个交互按钮/菜单:")
        print("-" * 70)
        for i, btn in enumerate(buttons):
            print(f"  按钮 {i+1}:")
            print(f"    位置: ({btn['x']}, {btn['y']})")
            print(f"    尺寸: {btn['width']}x{btn['height']}")
            print(f"    中心点: ({btn['center_x']}, {btn['center_y']}) 👆 点击这里")
            print(f"    颜色: {btn['color']}")
            print()
    
    # 6. 生成可视化图像
    print("\n🎨 生成可视化图像...")
    result = img.copy()
    
    # 绘制列表项
    for item in list_items:
        cv2.line(result, (0, item['y_start']), (width, item['y_start']), (0, 255, 0), 2)
        cv2.putText(result, f"Item {item['index']}", (10, item['center_y']),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # 绘制按钮
    for i, btn in enumerate(buttons):
        cv2.rectangle(result, (btn['x'], btn['y']), 
                     (btn['x'] + btn['width'], btn['y'] + btn['height']),
                     (0, 0, 255), 3)
        cv2.circle(result, (btn['center_x'], btn['center_y']), 8, (255, 0, 0), -1)
        cv2.putText(result, f"Btn{i+1}", (btn['x'], btn['y'] - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # 添加说明
    cv2.putText(result, "Green: List Items | Red: Buttons/Menus | Blue dot: Click point",
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    output_path = 'list_structure_analyzed.png'
    cv2.imwrite(output_path, result)
    print(f"✅ 可视化结果已保存: {output_path}")
    
    # 7. 生成JSON报告
    # 转换numpy类型为Python原生类型
    def convert_numpy(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(item) for item in obj]
        return obj
    
    report = {
        'image': {
            'path': image_path,
            'width': int(width),
            'height': int(height)
        },
        'list_items': convert_numpy(list_items),
        'buttons': convert_numpy(buttons),
        'summary': {
            'total_list_items': len(list_items),
            'total_buttons': len(buttons),
            'total_text_regions': len(text_regions)
        }
    }
    
    json_path = 'list_structure_report.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON报告已保存: {json_path}")
    
    # 8. 生成点击坐标脚本
    print("\n📝 生成自动点击脚本...")
    script_content = f"""#!/usr/bin/env python3
# 自动生成的点击坐标脚本
# 基于图片: {image_path}

import pyautogui
import time

# 检测到的按钮坐标
buttons = {json.dumps(buttons, indent=4)}

def click_button(button_index):
    \"\"\"点击指定按钮\"\"\"
    if 0 <= button_index < len(buttons):
        btn = buttons[button_index]
        print(f"点击按钮 {{button_index + 1}}: {{btn['color']}} at ({{btn['center_x']}}, {{btn['center_y']}})")
        
        # 注意：这些是图片中的相对坐标
        # 需要加上图片在屏幕上的偏移量
        # pyautogui.moveTo(screen_x + btn['center_x'], screen_y + btn['center_y'])
        # pyautogui.click()
    else:
        print(f"错误: 按钮索引超出范围 (0-{{len(buttons)-1}})")

if __name__ == '__main__':
    print("检测到 {{}} 个按钮:".format(len(buttons)))
    for i, btn in enumerate(buttons):
        print(f"  {{i}}: {{btn['color']}}按钮 at ({{btn['center_x']}}, {{btn['center_y']}})")
    print("\\n使用示例:")
    print("  click_button(0)  # 点击第一个按钮")
"""
    
    with open('auto_click_script.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    print("✅ 点击脚本已生成: auto_click_script.py")
    
    return report


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python analyze_list_structure.py <图片路径>")
        print("示例: python analyze_list_structure.py lists.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    analyze_list_structure(image_path)
    
    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)
    print("\n生成的文件:")
    print("  1. list_structure_analyzed.png  - 可视化结果（标注了所有元素）")
    print("  2. list_structure_report.json   - JSON格式的详细报告")
    print("  3. auto_click_script.py         - 自动点击脚本")
    print("\n查看可视化结果可以了解图片中的列表结构和可点击位置！")


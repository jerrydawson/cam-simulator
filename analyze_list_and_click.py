#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片列表结构分析和自动点击工具
分析图片中的列表结构，识别菜单项并自动点击
"""

import cv2
import numpy as np
import pyautogui
from PIL import Image
import time


class ListAnalyzer:
    def __init__(self, image_path):
        """初始化列表分析器"""
        self.image_path = image_path
        self.image = None
        self.gray = None
        self.items = []
        
    def load_image(self):
        """加载图片"""
        # 使用OpenCV加载
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            # 尝试使用PIL加载
            pil_img = Image.open(self.image_path)
            self.image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        print(f"图片已加载: {self.image.shape[1]}x{self.image.shape[0]}")
        
    def detect_list_items(self):
        """检测列表项"""
        print("\n正在分析列表结构...")
        
        # 边缘检测
        edges = cv2.Canny(self.gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选矩形区域（可能是列表项）
        list_items = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 筛选条件：宽度足够大，高度合理
            if w > 100 and 20 < h < 150:
                list_items.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                })
        
        # 按Y坐标排序（从上到下）
        list_items.sort(key=lambda item: item['y'])
        
        self.items = list_items
        print(f"检测到 {len(list_items)} 个可能的列表项")
        
        return list_items
    
    def detect_buttons_and_menus(self):
        """检测按钮和菜单"""
        print("\n正在检测按钮和菜单...")
        
        # 使用模板匹配或颜色检测来识别按钮
        # 这里使用简单的矩形检测
        
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 检测常见的按钮颜色（蓝色、绿色等）
        buttons = []
        
        # 蓝色范围
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # 绿色范围
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        
        # 合并遮罩
        mask = cv2.bitwise_or(mask_blue, mask_green)
        
        # 查找按钮轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 30 and h > 15:  # 最小按钮尺寸
                buttons.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'type': 'button'
                })
        
        print(f"检测到 {len(buttons)} 个可能的按钮/菜单")
        return buttons
    
    def visualize_detection(self, output_path='detected_items.png'):
        """可视化检测结果"""
        result = self.image.copy()
        
        # 绘制列表项
        for i, item in enumerate(self.items):
            cv2.rectangle(result, 
                         (item['x'], item['y']), 
                         (item['x'] + item['width'], item['y'] + item['height']),
                         (0, 255, 0), 2)
            cv2.putText(result, f"Item {i+1}", 
                       (item['x'] + 5, item['y'] + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(result, (item['center_x'], item['center_y']), 5, (0, 0, 255), -1)
        
        cv2.imwrite(output_path, result)
        print(f"\n检测结果已保存: {output_path}")
        
    def print_structure(self):
        """打印列表结构"""
        print("\n=== 列表结构分析 ===")
        print(f"图片尺寸: {self.image.shape[1]}x{self.image.shape[0]}")
        print(f"\n检测到 {len(self.items)} 个列表项:")
        print("-" * 60)
        
        for i, item in enumerate(self.items):
            print(f"项目 {i+1}:")
            print(f"  位置: ({item['x']}, {item['y']})")
            print(f"  尺寸: {item['width']}x{item['height']}")
            print(f"  中心点: ({item['center_x']}, {item['center_y']})")
            print()


def find_image_on_screen(template_path, confidence=0.8):
    """在屏幕上查找图片"""
    try:
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return center
    except Exception as e:
        print(f"查找图片失败: {e}")
    return None


def click_menu_item(item_index=1, image_path='lists.png'):
    """点击指定的菜单项"""
    print(f"\n准备点击第 {item_index} 个菜单项...")
    
    # 首先在屏幕上找到这个列表
    print("正在屏幕上查找列表...")
    location = find_image_on_screen(image_path, confidence=0.7)
    
    if location:
        print(f"找到列表位置: {location}")
        
        # 分析列表结构
        analyzer = ListAnalyzer(image_path)
        analyzer.load_image()
        items = analyzer.detect_list_items()
        
        if item_index <= len(items):
            item = items[item_index - 1]
            
            # 计算屏幕上的实际位置
            screen_x = location[0] + item['center_x'] - analyzer.image.shape[1] // 2
            screen_y = location[1] + item['center_y'] - analyzer.image.shape[0] // 2
            
            print(f"移动鼠标到: ({screen_x}, {screen_y})")
            
            # 移动鼠标并点击
            pyautogui.moveTo(screen_x, screen_y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            
            print("点击完成！")
        else:
            print(f"错误: 只检测到 {len(items)} 个项目")
    else:
        print("错误: 在屏幕上未找到列表")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='分析图片列表结构并自动点击')
    parser.add_argument('image', nargs='?', default='lists.png', help='图片路径')
    parser.add_argument('--analyze', action='store_true', help='只分析不点击')
    parser.add_argument('--click', type=int, help='点击第N个菜单项')
    parser.add_argument('--visualize', action='store_true', help='可视化检测结果')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("列表结构分析和自动点击工具")
    print("=" * 60)
    
    # 创建分析器
    analyzer = ListAnalyzer(args.image)
    analyzer.load_image()
    
    # 检测列表项
    analyzer.detect_list_items()
    
    # 检测按钮
    analyzer.detect_buttons_and_menus()
    
    # 打印结构
    analyzer.print_structure()
    
    # 可视化
    if args.visualize:
        analyzer.visualize_detection()
        print("\n提示: 检查 detected_items.png 查看检测结果")
    
    # 自动点击
    if args.click:
        print(f"\n将在3秒后点击第 {args.click} 个菜单项...")
        print("请确保列表在屏幕上可见！")
        time.sleep(3)
        click_menu_item(args.click, args.image)
    
    if not args.analyze and not args.click and not args.visualize:
        print("\n用法示例:")
        print("  python analyze_list_and_click.py lists.png --analyze")
        print("  python analyze_list_and_click.py lists.png --visualize")
        print("  python analyze_list_and_click.py lists.png --click 1")


if __name__ == '__main__':
    main()


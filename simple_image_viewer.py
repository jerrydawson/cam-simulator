#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单图片查看器
显示图片并标注可点击区域
"""

import cv2
import numpy as np
from PIL import Image
import sys


def show_image_with_grid(image_path):
    """显示图片并添加网格"""
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    height, width = img.shape[:2]
    print(f"图片尺寸: {width}x{height}")
    
    # 创建副本用于绘制
    display = img.copy()
    
    # 添加网格
    grid_size = 50
    for y in range(0, height, grid_size):
        cv2.line(display, (0, y), (width, y), (200, 200, 200), 1)
    for x in range(0, width, grid_size):
        cv2.line(display, (x, 0), (x, height), (200, 200, 200), 1)
    
    # 显示图片
    cv2.namedWindow('Image Viewer', cv2.WINDOW_NORMAL)
    cv2.imshow('Image Viewer', display)
    
    print("\n操作说明:")
    print("  - 鼠标点击可以查看坐标")
    print("  - 按 'q' 退出")
    print("  - 按 's' 保存标注后的图片")
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"点击位置: ({x}, {y})")
            # 在点击位置画圆
            cv2.circle(display, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Image Viewer', display)
    
    cv2.setMouseCallback('Image Viewer', mouse_callback)
    
    key = cv2.waitKey(0)
    if key == ord('s'):
        output = 'annotated_' + image_path
        cv2.imwrite(output, display)
        print(f"已保存标注图片: {output}")
    
    cv2.destroyAllWindows()


def analyze_image_structure(image_path):
    """分析图片结构"""
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    height, width = img.shape[:2]
    
    print("=" * 60)
    print("图片结构分析")
    print("=" * 60)
    print(f"文件: {image_path}")
    print(f"尺寸: {width}x{height}")
    print(f"通道数: {img.shape[2] if len(img.shape) > 2 else 1}")
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 边缘检测
    edges = cv2.Canny(gray, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"\n检测到的形状数量: {len(contours)}")
    
    # 分析主要的矩形区域
    rectangles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 20:  # 过滤小区域
            rectangles.append((x, y, w, h))
    
    rectangles.sort(key=lambda r: r[1])  # 按Y坐标排序
    
    print(f"\n主要区域 (可能的列表项/按钮):")
    print("-" * 60)
    for i, (x, y, w, h) in enumerate(rectangles[:20]):  # 只显示前20个
        print(f"{i+1:2d}. 位置: ({x:4d}, {y:4d})  尺寸: {w:4d}x{h:3d}  中心: ({x+w//2:4d}, {y+h//2:4d})")
    
    # 创建可视化
    result = img.copy()
    for i, (x, y, w, h) in enumerate(rectangles[:20]):
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(result, str(i+1), (x+5, y+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imwrite('analyzed_structure.png', result)
    print(f"\n结构分析图已保存: analyzed_structure.png")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python simple_image_viewer.py <图片路径> [--analyze]")
        print("\n示例:")
        print("  python simple_image_viewer.py lists.png")
        print("  python simple_image_viewer.py lists.png --analyze")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == '--analyze':
        analyze_image_structure(image_path)
    else:
        show_image_with_grid(image_path)


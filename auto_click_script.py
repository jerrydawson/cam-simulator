#!/usr/bin/env python3
# 自动生成的点击坐标脚本
# 基于图片: lists.png

import pyautogui
import time

# 检测到的按钮坐标
buttons = [
    {
        "x": 629,
        "y": 247,
        "width": 73,
        "height": 48,
        "center_x": 665,
        "center_y": 271,
        "color": "\u7ea2\u8272",
        "area": 3357.0
    },
    {
        "x": 629,
        "y": 437,
        "width": 73,
        "height": 48,
        "center_x": 665,
        "center_y": 461,
        "color": "\u7ea2\u8272",
        "area": 3346.0
    },
    {
        "x": 629,
        "y": 627,
        "width": 73,
        "height": 48,
        "center_x": 665,
        "center_y": 651,
        "color": "\u7ea2\u8272",
        "area": 3357.0
    },
    {
        "x": 629,
        "y": 817,
        "width": 73,
        "height": 49,
        "center_x": 665,
        "center_y": 841,
        "color": "\u7ea2\u8272",
        "area": 3418.0
    },
    {
        "x": 0,
        "y": 907,
        "width": 837,
        "height": 63,
        "center_x": 418,
        "center_y": 938,
        "color": "\u6a59\u8272",
        "area": 1811.0
    }
]

def click_button(button_index):
    """点击指定按钮"""
    if 0 <= button_index < len(buttons):
        btn = buttons[button_index]
        print(f"点击按钮 {button_index + 1}: {btn['color']} at ({btn['center_x']}, {btn['center_y']})")
        
        # 注意：这些是图片中的相对坐标
        # 需要加上图片在屏幕上的偏移量
        # pyautogui.moveTo(screen_x + btn['center_x'], screen_y + btn['center_y'])
        # pyautogui.click()
    else:
        print(f"错误: 按钮索引超出范围 (0-{len(buttons)-1})")

if __name__ == '__main__':
    print("检测到 {} 个按钮:".format(len(buttons)))
    for i, btn in enumerate(buttons):
        print(f"  {i}: {btn['color']}按钮 at ({btn['center_x']}, {btn['center_y']})")
    print("\n使用示例:")
    print("  click_button(0)  # 点击第一个按钮")

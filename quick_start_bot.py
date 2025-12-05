#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 简化版自动学习机器人
无需复杂配置，直接运行
"""

import pyautogui
import time
from PIL import ImageGrab
import re
import os

# 尝试导入OCR
try:
    import pytesseract
    HAS_OCR = True
except:
    HAS_OCR = False


class SimpleBot:
    def __init__(self):
        # 一级菜单坐标（需要先找到窗口位置）
        self.menus = [
            (665, 271), (665, 461), (665, 651), (665, 841)
        ]
        self.offset_x = 0
        self.offset_y = 0
        
    def find_window(self):
        """简单的窗口查找"""
        print("=" * 60)
        print("🔍 查找课程列表窗口")
        print("=" * 60)
        print("\n请按以下步骤操作:")
        print("1. 打开浏览器，进入课程页面")
        print("2. 将鼠标移动到课程列表的左上角")
        print("3. 5秒后程序会自动记录位置\n")
        
        for i in range(5, 0, -1):
            print(f"   {i}秒后开始记录...", end='\r')
            time.sleep(1)
        
        pos = pyautogui.position()
        self.offset_x = pos[0]
        self.offset_y = pos[1]
        
        print(f"\n✅ 窗口位置已记录: ({self.offset_x}, {self.offset_y})")
        return True
    
    def click(self, x, y):
        """点击相对位置"""
        abs_x = self.offset_x + x
        abs_y = self.offset_y + y
        pyautogui.moveTo(abs_x, abs_y, duration=0.3)
        pyautogui.click()
    
    def screenshot_region(self, x, y, w, h):
        """截取区域"""
        abs_x = self.offset_x + x
        abs_y = self.offset_y + y
        bbox = (abs_x, abs_y, abs_x + w, abs_y + h)
        return ImageGrab.grab(bbox=bbox)
    
    def extract_hours(self, image):
        """提取学时信息"""
        if not HAS_OCR:
            print("   ⚠️  未安装OCR，无法自动识别")
            return []
        
        try:
            text = pytesseract.image_to_string(image, lang='chi_sim')
            pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
            matches = re.findall(pattern, text)
            
            results = []
            for c, t in matches:
                if float(c) < float(t):
                    results.append(f"{c}/{t}学时")
            
            return results
        except:
            return []
    
    def process_menu(self, menu_num):
        """处理一个菜单"""
        print(f"\n{'='*60}")
        print(f"📚 处理菜单 {menu_num}")
        print(f"{'='*60}")
        
        # 点击一级菜单
        x, y = self.menus[menu_num - 1]
        print(f"1️⃣  点击菜单按钮...")
        self.click(x, y)
        time.sleep(1.5)
        
        # 截图二级菜单区域
        print(f"2️⃣  截图分析...")
        y_start = 300 + (menu_num - 1) * 190
        screenshot = self.screenshot_region(50, y_start, 500, 120)
        screenshot.save(f'menu_{menu_num}_screenshot.png')
        print(f"   保存截图: menu_{menu_num}_screenshot.png")
        
        # 识别学时
        print(f"3️⃣  识别学时信息...")
        incomplete = self.extract_hours(screenshot)
        
        if incomplete:
            print(f"   找到 {len(incomplete)} 个未完成课程:")
            for course in incomplete:
                print(f"      - {course}")
        else:
            print(f"   未识别到未完成课程")
        
        return len(incomplete)
    
    def run(self):
        """运行"""
        print("\n" + "🎓 " * 20)
        print("简易自动学习机器人")
        print("🎓 " * 20 + "\n")
        
        if not HAS_OCR:
            print("⚠️  警告: pytesseract未安装")
            print("   只能截图，无法自动识别学时")
            print("   安装: pip install pytesseract\n")
        
        # 查找窗口
        if not self.find_window():
            return
        
        print("\n准备开始处理...")
        time.sleep(2)
        
        # 处理所有菜单
        total = 0
        for i in range(1, 5):
            try:
                count = self.process_menu(i)
                total += count
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n\n用户中断")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                continue
        
        print("\n" + "="*60)
        print(f"✅ 完成！共处理 {total} 个未完成课程")
        print(f"📁 截图已保存到当前目录")
        print("="*60)


if __name__ == '__main__':
    bot = SimpleBot()
    bot.run()


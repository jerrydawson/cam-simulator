#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动学习机器人
自动截屏、OCR识别、判断并点击未完成课程
"""

import pyautogui
import time
import cv2
import numpy as np
from PIL import Image, ImageGrab
import re
import os
from datetime import datetime

# 尝试导入OCR库
try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("⚠️  警告: pytesseract未安装，将使用备用识别方法")
    print("   安装: pip install pytesseract")


class AutoLearningBot:
    def __init__(self, base_image='lists.png'):
        """初始化自动学习机器人"""
        self.base_image = base_image
        self.window_offset_x = 0
        self.window_offset_y = 0
        
        # 一级菜单坐标（红色按钮）
        self.level1_menus = [
            {'id': 1, 'x': 665, 'y': 271},
            {'id': 2, 'x': 665, 'y': 461},
            {'id': 3, 'x': 665, 'y': 651},
            {'id': 4, 'x': 665, 'y': 841},
        ]
        
        # 二级菜单区域（相对于一级菜单的偏移）
        self.level2_regions = {
            1: {'x': 50, 'y': 305, 'width': 500, 'height': 123},
            2: {'x': 50, 'y': 494, 'width': 500, 'height': 123},
            3: {'x': 50, 'y': 685, 'width': 500, 'height': 123},
            4: {'x': 50, 'y': 875, 'width': 500, 'height': 95},
        }
        
        self.log_file = f"learning_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def find_window(self):
        """在屏幕上查找课程列表窗口"""
        self.log("正在查找课程列表窗口...")
        
        try:
            # 尝试在屏幕上定位基准图片
            location = pyautogui.locateOnScreen(self.base_image, confidence=0.6)
            
            if location:
                self.window_offset_x = location.left
                self.window_offset_y = location.top
                self.log(f"✅ 找到窗口位置: ({self.window_offset_x}, {self.window_offset_y})")
                return True
            else:
                self.log("❌ 未找到窗口，尝试备用方法...")
                # 备用：让用户手动点击
                self.log("请将鼠标移动到课程列表左上角，5秒后自动记录位置...")
                time.sleep(5)
                pos = pyautogui.position()
                self.window_offset_x = pos[0]
                self.window_offset_y = pos[1]
                self.log(f"✅ 手动设置窗口位置: ({self.window_offset_x}, {self.window_offset_y})")
                return True
                
        except Exception as e:
            self.log(f"❌ 查找窗口失败: {e}")
            return False
    
    def click_point(self, x, y, duration=0.3, delay=0.5):
        """点击指定位置"""
        abs_x = self.window_offset_x + x
        abs_y = self.window_offset_y + y
        
        self.log(f"   点击: ({abs_x}, {abs_y})")
        pyautogui.moveTo(abs_x, abs_y, duration=duration)
        pyautogui.click()
        time.sleep(delay)
    
    def capture_region(self, x, y, width, height, save_path=None):
        """截取指定区域"""
        abs_x = self.window_offset_x + x
        abs_y = self.window_offset_y + y
        
        # 截图
        bbox = (abs_x, abs_y, abs_x + width, abs_y + height)
        screenshot = ImageGrab.grab(bbox=bbox)
        
        if save_path:
            screenshot.save(save_path)
            self.log(f"   截图保存: {save_path}")
        
        return screenshot
    
    def ocr_extract_hours(self, image):
        """使用OCR提取学时信息"""
        if not HAS_OCR:
            return []
        
        try:
            # 转换为灰度图提高识别率
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # OCR识别
            # 配置：只识别数字、小数点、斜杠和中文
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(binary, lang='chi_sim+eng', config=custom_config)
            
            self.log(f"   OCR识别文本: {text[:100]}...")
            
            # 提取学时信息：x.x/x.x学时 或 x/x学时
            pattern = r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\s*学时'
            matches = re.findall(pattern, text)
            
            results = []
            for completed, total in matches:
                try:
                    c = float(completed)
                    t = float(total)
                    results.append({
                        'completed': c,
                        'total': t,
                        'is_incomplete': c < t,
                        'text': f"{c}/{t}学时"
                    })
                except ValueError:
                    continue
            
            return results
            
        except Exception as e:
            self.log(f"   OCR错误: {e}")
            return []
    
    def detect_text_regions_opencv(self, image):
        """使用OpenCV检测文本区域（备用方法）"""
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 膨胀连接文本
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 学时文本特征：宽度较大，高度适中
            if 80 < w < 300 and 15 < h < 40:
                text_regions.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                })
        
        return text_regions
    
    def find_incomplete_courses(self, menu_id):
        """查找未完成的课程"""
        self.log(f"\n>>> 分析菜单 {menu_id} 的课程...")
        
        # 获取二级菜单区域
        region = self.level2_regions[menu_id]
        
        # 截图
        timestamp = datetime.now().strftime('%H%M%S')
        screenshot_path = f"screenshot_menu{menu_id}_{timestamp}.png"
        screenshot = self.capture_region(
            region['x'], region['y'], 
            region['width'], region['height'],
            save_path=screenshot_path
        )
        
        # OCR识别学时
        hours_info = self.ocr_extract_hours(screenshot)
        
        if hours_info:
            self.log(f"   找到 {len(hours_info)} 个课程:")
            incomplete_courses = []
            
            for i, info in enumerate(hours_info):
                status = "❌ 未完成" if info['is_incomplete'] else "✅ 已完成"
                self.log(f"   课程 {i+1}: {info['text']} - {status}")
                
                if info['is_incomplete']:
                    incomplete_courses.append(info)
            
            return incomplete_courses, hours_info
        else:
            self.log("   ⚠️  未识别到学时信息")
            
            # 备用：检测文本区域
            text_regions = self.detect_text_regions_opencv(screenshot)
            self.log(f"   检测到 {len(text_regions)} 个可能的文本区域")
            
            return [], []
    
    def click_incomplete_course(self, menu_id, course_index, hours_info):
        """点击未完成的课程"""
        region = self.level2_regions[menu_id]
        
        # 估计课程的Y位置（假设每个课程约40-50px高）
        # 第一个课程在区域顶部，后续课程依次向下
        item_height = 45
        start_y = region['y'] + 30
        
        click_x = region['x'] + 150  # 学时文本大概在左侧150px处
        click_y = start_y + course_index * item_height
        
        self.log(f"   点击课程 {course_index + 1}")
        self.click_point(click_x, click_y, duration=0.5, delay=1.0)
        
        return True
    
    def process_level1_menu(self, menu_id):
        """处理一个一级菜单"""
        self.log(f"\n{'='*60}")
        self.log(f"处理一级菜单 {menu_id}")
        self.log(f"{'='*60}")
        
        # 点击一级菜单按钮
        menu = self.level1_menus[menu_id - 1]
        self.log("步骤1: 点击一级菜单展开")
        self.click_point(menu['x'], menu['y'], delay=1.5)
        
        # 等待菜单展开
        self.log("步骤2: 等待二级菜单展开...")
        time.sleep(1.0)
        
        # 查找未完成课程
        self.log("步骤3: 截图并分析学时信息")
        incomplete_courses, all_courses = self.find_incomplete_courses(menu_id)
        
        if not incomplete_courses:
            self.log("   ✅ 所有课程已完成或未检测到课程")
            return 0
        
        # 点击未完成课程
        self.log(f"步骤4: 处理 {len(incomplete_courses)} 个未完成课程")
        
        for i, course in enumerate(incomplete_courses):
            self.log(f"\n   >>> 学习课程: {course['text']}")
            
            # 找到这个课程在列表中的索引
            course_index = all_courses.index(course)
            
            # 点击课程
            self.click_incomplete_course(menu_id, course_index, all_courses)
            
            # 等待视频开始播放
            self.log("   等待视频加载...")
            time.sleep(3)
            
            # 这里可以添加等待视频播放完成的逻辑
            # 简化版：固定等待时间
            video_duration = int(course['total'] * 60)  # 假设1学时=60秒
            self.log(f"   预计学习时长: {video_duration} 秒")
            
            # TODO: 实际应用中可以通过截图检测播放完成
            # time.sleep(video_duration)
            
            self.log("   ⏭️  跳过等待（测试模式）")
            
            # 返回列表
            pyautogui.press('esc')
            time.sleep(1)
        
        return len(incomplete_courses)
    
    def run(self, menu_ids=None, test_mode=False):
        """运行自动学习"""
        self.log("=" * 60)
        self.log("🎓 自动学习机器人启动")
        self.log("=" * 60)
        
        # 检查OCR
        if not HAS_OCR:
            self.log("⚠️  警告: 未安装OCR库，识别可能不准确")
            self.log("   建议安装: pip install pytesseract")
            self.log("   并安装系统依赖: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        
        # 查找窗口
        if not self.find_window():
            self.log("❌ 无法找到窗口，程序退出")
            return
        
        # 确定要处理的菜单
        if menu_ids is None:
            menu_ids = [1, 2, 3, 4]  # 处理所有菜单
        
        self.log(f"\n将处理 {len(menu_ids)} 个菜单: {menu_ids}")
        
        if test_mode:
            self.log("⚠️  测试模式：不会实际等待视频播放")
        
        self.log("\n准备开始... 3秒后启动")
        time.sleep(3)
        
        # 处理每个菜单
        total_processed = 0
        
        for menu_id in menu_ids:
            try:
                count = self.process_level1_menu(menu_id)
                total_processed += count
                
                # 菜单之间的间隔
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.log("\n⚠️  用户中断")
                break
            except Exception as e:
                self.log(f"❌ 处理菜单 {menu_id} 时出错: {e}")
                import traceback
                self.log(traceback.format_exc())
                continue
        
        # 完成
        self.log("\n" + "=" * 60)
        self.log("✅ 自动学习完成")
        self.log(f"   处理了 {total_processed} 个未完成课程")
        self.log(f"   日志文件: {self.log_file}")
        self.log("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动学习机器人')
    parser.add_argument('--menu', type=int, nargs='+', 
                       help='指定要处理的菜单ID (1-4)，默认处理所有')
    parser.add_argument('--test', action='store_true',
                       help='测试模式：不等待视频播放')
    parser.add_argument('--base-image', default='lists.png',
                       help='基准图片路径')
    
    args = parser.parse_args()
    
    # 创建机器人
    bot = AutoLearningBot(base_image=args.base_image)
    
    # 运行
    try:
        bot.run(menu_ids=args.menu, test_mode=args.test)
    except KeyboardInterrupt:
        print("\n\n程序被用户终止")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()


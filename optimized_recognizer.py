#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的识别器
基于特征分析结果，提供高准确率的元素识别
"""

import cv2
import numpy as np
from PIL import Image
import re

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class OptimizedRecognizer:
    """
    优化的识别器
    
    基于lists_full.png的特征分析：
    - 图片尺寸: 866x2056
    - 红色区域: 15个 (0.77%) - 一级菜单按钮
    - 文本区域: 276个，平均高度19.5px
    - 水平分隔线: 29条，平均间距69.1px
    - 列表项: 约29个
    """
    
    def __init__(self):
        # 颜色识别参数（HSV）
        self.color_ranges = {
            '红色': {
                'lower1': np.array([0, 100, 100]),
                'upper1': np.array([10, 255, 255]),
                'lower2': np.array([160, 100, 100]),
                'upper2': np.array([180, 255, 255]),
                'min_area': 500,
                'description': '一级菜单按钮'
            },
            '橙色': {
                'lower': np.array([10, 100, 100]),
                'upper': np.array([25, 255, 255]),
                'min_area': 200,
                'description': '底部按钮'
            },
            '蓝色': {
                'lower': np.array([85, 100, 100]),
                'upper': np.array([125, 255, 255]),
                'min_area': 200,
                'description': '链接或提示'
            }
        }
        
        # 文本识别参数
        self.text_config = {
            'avg_height': 19.5,
            'height_range': (15, 25),
            'aspect_ratio_range': (2, 20),
            'min_width': 80
        }
        
        # 按钮识别参数
        self.button_config = {
            'min_area': 200,
            'max_area': 10000,
            'aspect_ratio_range': (0.5, 2.5),
            'width_range': (20, 200),
            'height_range': (20, 80)
        }
        
        # 列表结构参数
        self.list_config = {
            'avg_spacing': 69.1,
            'spacing_tolerance': 20,
            'estimated_items': 29
        }
    
    def detect_red_buttons(self, image):
        """
        检测红色按钮（一级菜单）
        
        优化点：
        - 使用精确的HSV范围
        - 面积过滤（>500px²）
        - 去重处理
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 红色有两个HSV范围
        config = self.color_ranges['红色']
        mask1 = cv2.inRange(hsv, config['lower1'], config['upper1'])
        mask2 = cv2.inRange(hsv, config['lower2'], config['upper2'])
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # 形态学处理，去噪
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < config['min_area']:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # 按钮特征验证
            if w < 30 or h < 30:
                continue
            
            buttons.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'center_x': x + w // 2,
                'center_y': y + h // 2,
                'area': int(area),
                'type': 'level1_menu',
                'color': '红色'
            })
        
        # 按Y坐标排序
        buttons.sort(key=lambda b: b['y'])
        
        # 去重（Y坐标相近的合并）
        unique_buttons = []
        for btn in buttons:
            is_duplicate = False
            for existing in unique_buttons:
                if abs(btn['center_y'] - existing['center_y']) < 30 and \
                   abs(btn['center_x'] - existing['center_x']) < 30:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_buttons.append(btn)
        
        return unique_buttons
    
    def extract_text_with_preprocessing(self, image, region):
        """
        带预处理的文本提取
        
        优化点：
        - 灰度化
        - 对比度增强
        - 二值化
        - 降噪
        - 尺寸归一化
        """
        if not HAS_OCR:
            return None
        
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        roi = image[y:y+h, x:x+w]
        
        # 1. 灰度化
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # 2. 对比度增强（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 3. 二值化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 4. 降噪
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # 5. 尺寸归一化（放大到标准高度）
        target_height = 40
        scale = target_height / h
        new_width = int(w * scale)
        resized = cv2.resize(denoised, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
        
        # 6. OCR识别
        try:
            # 配置：只识别数字、斜杠、小数点和中文
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789./学时'
            text = pytesseract.image_to_string(resized, lang='chi_sim', config=custom_config)
            return text.strip()
        except Exception as e:
            return None
    
    def detect_hours_pattern(self, image, save_debug=False):
        """
        检测学时模式
        
        优化点：
        - 先检测可能的文本区域
        - 只对有希望的区域进行OCR
        - 使用正则精确匹配
        """
        if not HAS_OCR:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用MSER检测文本区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # 筛选可能包含学时信息的区域
        text_regions = []
        for region in regions:
            if len(region) < 10:
                continue
            
            x, y, w, h = cv2.boundingRect(region)
            
            # 学时文本特征：宽度较大，高度适中
            cfg = self.text_config
            if cfg['height_range'][0] < h < cfg['height_range'][1] and w > cfg['min_width']:
                aspect_ratio = w / h
                if cfg['aspect_ratio_range'][0] < aspect_ratio < cfg['aspect_ratio_range'][1]:
                    text_regions.append({'x': x, 'y': y, 'width': w, 'height': h})
        
        # 去重（合并重叠区域）
        text_regions = self._merge_overlapping_regions(text_regions)
        
        # 对每个区域进行OCR
        hours_data = []
        debug_img = image.copy() if save_debug else None
        
        for i, region in enumerate(text_regions):
            text = self.extract_text_with_preprocessing(image, region)
            
            if text:
                # 匹配学时模式
                pattern = r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\s*学时'
                matches = re.findall(pattern, text)
                
                if matches:
                    for completed, total in matches:
                        try:
                            c = float(completed)
                            t = float(total)
                            
                            hours_data.append({
                                'completed': c,
                                'total': t,
                                'incomplete': c < t,
                                'text': f"{c}/{t}学时",
                                'region': region,
                                'confidence': 'high'
                            })
                            
                            # 调试：标注识别到的区域
                            if save_debug:
                                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                                color = (0, 0, 255) if c < t else (0, 255, 0)
                                cv2.rectangle(debug_img, (x, y), (x+w, y+h), color, 2)
                                cv2.putText(debug_img, f"{c}/{t}", (x, y-5),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        except ValueError:
                            pass
        
        if save_debug and debug_img is not None:
            cv2.imwrite('hours_detection_debug.png', debug_img)
        
        return hours_data
    
    def _merge_overlapping_regions(self, regions):
        """合并重叠的区域"""
        if not regions:
            return []
        
        # 按Y坐标排序
        regions.sort(key=lambda r: r['y'])
        
        merged = []
        for region in regions:
            if not merged:
                merged.append(region)
                continue
            
            # 检查是否与最后一个区域重叠
            last = merged[-1]
            
            # 计算重叠
            x_overlap = (region['x'] < last['x'] + last['width'] and 
                        region['x'] + region['width'] > last['x'])
            y_overlap = (region['y'] < last['y'] + last['height'] and 
                        region['y'] + region['height'] > last['y'])
            
            if x_overlap and y_overlap:
                # 合并
                x1 = min(last['x'], region['x'])
                y1 = min(last['y'], region['y'])
                x2 = max(last['x'] + last['width'], region['x'] + region['width'])
                y2 = max(last['y'] + last['height'], region['y'] + region['height'])
                
                merged[-1] = {
                    'x': x1,
                    'y': y1,
                    'width': x2 - x1,
                    'height': y2 - y1
                }
            else:
                merged.append(region)
        
        return merged
    
    def detect_list_items(self, image):
        """
        检测列表项
        
        优化点：
        - 基于水平分隔线
        - 考虑平均间距
        - 区分一级和二级列表
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = image.shape[:2]
        
        # 检测水平线
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 2, 1))
        detect_horizontal = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, horizontal_kernel)
        edges = cv2.Canny(detect_horizontal, 50, 150)
        
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                               minLineLength=width//3, maxLineGap=20)
        
        horizontal_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 5:  # 水平线
                    horizontal_lines.append({
                        'y': (y1 + y2) // 2,
                        'x1': x1,
                        'x2': x2,
                        'length': abs(x2 - x1)
                    })
        
        # 去重
        horizontal_lines.sort(key=lambda l: l['y'])
        unique_lines = []
        for line in horizontal_lines:
            if not unique_lines or abs(line['y'] - unique_lines[-1]['y']) > 10:
                unique_lines.append(line)
        
        # 根据分隔线划分列表项
        list_items = []
        for i in range(len(unique_lines) - 1):
            y_start = unique_lines[i]['y']
            y_end = unique_lines[i + 1]['y']
            item_height = y_end - y_start
            
            # 过滤太小的项
            if item_height > 30:
                list_items.append({
                    'index': len(list_items) + 1,
                    'y_start': y_start,
                    'y_end': y_end,
                    'height': item_height,
                    'center_y': (y_start + y_end) // 2
                })
        
        return list_items


def demo_recognition():
    """演示优化的识别"""
    print("=" * 60)
    print("优化识别演示")
    print("=" * 60)
    
    # 加载图片
    image = cv2.imread('lists_full.png')
    if image is None:
        print("❌ 无法加载图片")
        return
    
    print(f"✅ 图片已加载: {image.shape[1]}x{image.shape[0]}")
    
    # 创建识别器
    recognizer = OptimizedRecognizer()
    
    # 1. 检测红色按钮
    print("\n🔴 检测一级菜单按钮...")
    red_buttons = recognizer.detect_red_buttons(image)
    print(f"   找到 {len(red_buttons)} 个红色按钮")
    for i, btn in enumerate(red_buttons):
        print(f"   按钮 {i+1}: 位置({btn['center_x']}, {btn['center_y']}), 面积{btn['area']}px²")
    
    # 2. 检测列表项
    print("\n📋 检测列表结构...")
    list_items = recognizer.detect_list_items(image)
    print(f"   找到 {len(list_items)} 个列表项")
    for item in list_items[:5]:
        print(f"   项 {item['index']}: Y={item['y_start']}~{item['y_end']} (高度{item['height']}px)")
    
    # 3. 检测学时信息
    if HAS_OCR:
        print("\n⏰ 检测学时信息...")
        hours_data = recognizer.detect_hours_pattern(image, save_debug=True)
        print(f"   找到 {len(hours_data)} 个学时信息")
        
        incomplete = [h for h in hours_data if h['incomplete']]
        complete = [h for h in hours_data if not h['incomplete']]
        
        print(f"   未完成: {len(incomplete)} 个")
        print(f"   已完成: {len(complete)} 个")
        
        for i, h in enumerate(hours_data[:5]):
            status = "❌" if h['incomplete'] else "✅"
            print(f"   {i+1}. {h['text']} {status}")
    else:
        print("\n⚠️  OCR未安装，跳过学时检测")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成")
    print("=" * 60)


if __name__ == '__main__':
    demo_recognition()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二级菜单特征分析工具
专门分析展开后的课程列表（二级菜单）
"""

import cv2
import numpy as np
from PIL import Image
import json
import re

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class Level2MenuAnalyzer:
    """二级菜单分析器"""
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.level1_buttons = []
        self.level2_regions = []
        
    def load_image(self):
        """加载图片"""
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"无法加载图片: {self.image_path}")
        
        height, width = self.image.shape[:2]
        print(f"✅ 图片已加载: {width}x{height}")
        return self.image
    
    def detect_level1_buttons(self):
        """检测一级菜单按钮"""
        print("\n🔴 检测一级菜单按钮（红色）")
        print("-" * 60)
        
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
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 30 and h > 30:
                    buttons.append({
                        'id': len(buttons) + 1,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_y': y + h // 2,
                        'area': int(area)
                    })
        
        buttons.sort(key=lambda b: b['y'])
        
        # 去重
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
        
        print(f"   找到 {len(unique_buttons)} 个一级菜单按钮")
        for btn in unique_buttons:
            print(f"   按钮 {btn['id']}: Y={btn['center_y']}")
        
        return unique_buttons
    
    def estimate_level2_regions(self):
        """估计二级菜单区域"""
        print("\n📋 估计二级菜单区域")
        print("-" * 60)
        
        if not self.level1_buttons:
            self.detect_level1_buttons()
        
        height = self.image.shape[0]
        
        regions = []
        
        for i, btn in enumerate(self.level1_buttons):
            # 二级菜单在一级按钮下方
            y_start = btn['y'] + btn['height'] + 5
            
            # 确定结束位置
            if i + 1 < len(self.level1_buttons):
                y_end = self.level1_buttons[i + 1]['y'] - 5
            else:
                y_end = height - 100
            
            region_height = y_end - y_start
            
            if region_height > 40:
                # 估计课程数量（假设每个课程约45-70px高）
                avg_item_height = 55
                estimated_items = max(1, int(region_height / avg_item_height))
                
                region = {
                    'parent_button': btn['id'],
                    'x': 20,
                    'y_start': y_start,
                    'y_end': y_end,
                    'height': region_height,
                    'estimated_items': estimated_items
                }
                
                regions.append(region)
                
                print(f"\n   一级按钮 {btn['id']} 的二级菜单:")
                print(f"      Y范围: {y_start} ~ {y_end}")
                print(f"      高度: {region_height}px")
                print(f"      估计课程数: {estimated_items}")
        
        self.level2_regions = regions
        return regions
    
    def analyze_level2_items(self):
        """分析二级菜单项的特征"""
        print("\n🔍 分析二级菜单项特征")
        print("-" * 60)
        
        if not self.level2_regions:
            self.estimate_level2_regions()
        
        all_items = []
        
        for region in self.level2_regions:
            print(f"\n   === 一级按钮 {region['parent_button']} 的二级菜单 ===")
            
            # 提取该区域
            y_start = region['y_start']
            y_end = region['y_end']
            roi = self.image[y_start:y_end, :]
            
            # 分析该区域的特征
            items = self.detect_items_in_region(roi, y_start, region['parent_button'])
            
            all_items.extend(items)
            
            print(f"      实际检测到: {len(items)} 个课程项")
            
            for item in items[:3]:  # 显示前3个
                print(f"         课程 {item['item_id']}: Y={item['y']}, 高度={item['height']}px")
        
        print(f"\n   总计: {len(all_items)} 个二级菜单项")
        
        return all_items
    
    def detect_items_in_region(self, roi, offset_y, parent_id):
        """检测区域内的课程项"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 使用MSER检测文本区域
        mser = cv2.MSER_create()
        try:
            regions, _ = mser.detectRegions(gray)
        except:
            return []
        
        # 筛选课程项
        items = []
        processed_y = set()
        
        for region in regions:
            if len(region) < 20:
                continue
            
            x, y, w, h = cv2.boundingRect(region)
            
            # 课程项特征：
            # - 宽度较大（包含课程名和学时）
            # - 高度适中（30-70px）
            # - 横跨多列
            if w > 200 and 30 < h < 70:
                # 检查Y坐标是否已处理（去重）
                y_key = y // 20  # 20px容差
                if y_key not in processed_y:
                    processed_y.add(y_key)
                    
                    items.append({
                        'parent_menu': parent_id,
                        'item_id': len(items) + 1,
                        'x': x,
                        'y': offset_y + y,
                        'width': w,
                        'height': h,
                        'center_y': offset_y + y + h // 2
                    })
        
        # 按Y坐标排序
        items.sort(key=lambda i: i['y'])
        
        # 重新编号
        for i, item in enumerate(items):
            item['item_id'] = i + 1
        
        return items
    
    def detect_hours_text_positions(self):
        """检测学时文本的位置"""
        print("\n⏰ 检测学时文本位置")
        print("-" * 60)
        
        if not HAS_OCR:
            print("   ⚠️  pytesseract未安装，使用模式匹配")
            return self.detect_hours_by_pattern()
        
        # 对每个二级区域进行OCR
        hours_positions = []
        
        for region in self.level2_regions:
            y_start = region['y_start']
            y_end = region['y_end']
            
            # 提取区域
            roi = self.image[y_start:y_end, :]
            
            # OCR识别
            try:
                # 使用图像到数据，获取位置信息
                import pytesseract
                from pytesseract import Output
                
                data = pytesseract.image_to_data(roi, lang='chi_sim', output_type=Output.DICT)
                
                # 查找学时文本
                for i, text in enumerate(data['text']):
                    if not text.strip():
                        continue
                    
                    # 匹配学时模式
                    pattern = r'(\d+\.?\d*)/(\d+\.?\d*)学时'
                    if re.search(pattern, text):
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        conf = data['conf'][i]
                        
                        if int(conf) > 30:  # 置信度阈值
                            hours_positions.append({
                                'parent_menu': region['parent_button'],
                                'text': text,
                                'x': x,
                                'y': y_start + y,
                                'width': w,
                                'height': h,
                                'confidence': int(conf)
                            })
            except Exception as e:
                print(f"   OCR错误: {e}")
        
        print(f"   找到 {len(hours_positions)} 个学时文本")
        
        for i, pos in enumerate(hours_positions[:5]):
            print(f"      {i+1}. {pos['text']} at ({pos['x']}, {pos['y']})")
        
        return hours_positions
    
    def detect_hours_by_pattern(self):
        """通过模式检测学时文本（不使用OCR）"""
        # 基于颜色和位置特征估计学时文本位置
        hours_positions = []
        
        for region in self.level2_regions:
            # 学时文本通常在左侧或中间
            # 假设每个课程项约55px高
            y_start = region['y_start']
            num_items = region['estimated_items']
            
            for i in range(num_items):
                item_y = y_start + 30 + i * 55
                
                if item_y < region['y_end']:
                    hours_positions.append({
                        'parent_menu': region['parent_button'],
                        'estimated': True,
                        'x': 150,  # 估计位置
                        'y': item_y,
                        'click_x': 200,
                        'click_y': item_y
                    })
        
        print(f"   估计 {len(hours_positions)} 个学时文本位置")
        
        return hours_positions
    
    def analyze_text_color(self):
        """分析文本颜色特征"""
        print("\n🎨 分析文本颜色")
        print("-" * 60)
        
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 常见文本颜色
        color_ranges = {
            '黑色/深灰': ([0, 0, 0], [180, 255, 80]),
            '蓝色': ([100, 50, 50], [130, 255, 255]),
            '绿色': ([40, 50, 50], [80, 255, 255]),
        }
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixels = cv2.countNonZero(mask)
            percentage = (pixels / (self.image.shape[0] * self.image.shape[1])) * 100
            
            if percentage > 1:
                print(f"   {color_name}: {percentage:.1f}%")
    
    def create_level2_visualization(self):
        """创建二级菜单可视化"""
        print("\n🎨 生成二级菜单可视化")
        print("-" * 60)
        
        result = self.image.copy()
        
        # 绘制一级按钮
        for btn in self.level1_buttons:
            cv2.rectangle(result,
                         (btn['x'], btn['y']),
                         (btn['x'] + btn['width'], btn['y'] + btn['height']),
                         (0, 0, 255), 3)
            cv2.putText(result, f"L1-{btn['id']}", 
                       (btn['x'] - 60, btn['y'] + btn['height'] // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 绘制二级菜单区域
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        for i, region in enumerate(self.level2_regions):
            color = colors[i % len(colors)]
            
            # 绘制区域边界
            cv2.rectangle(result,
                         (10, region['y_start']),
                         (self.image.shape[1] - 10, region['y_end']),
                         color, 2)
            
            # 标注
            cv2.putText(result, f"L2-Menu{region['parent_button']} ({region['estimated_items']} items)", 
                       (20, region['y_start'] + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 绘制估计的课程项位置
            for j in range(region['estimated_items']):
                item_y = region['y_start'] + 30 + j * 55
                if item_y < region['y_end']:
                    # 课程项标记
                    cv2.circle(result, (50, item_y), 5, color, -1)
                    cv2.line(result, (50, item_y), (800, item_y), color, 1, cv2.LINE_AA)
                    
                    # 学时文本位置标记
                    cv2.circle(result, (200, item_y), 8, (0, 165, 255), -1)
        
        # 添加图例
        legend_y = 30
        cv2.putText(result, "Red box: L1 Menu | Colored box: L2 Region | Orange dot: Hours text", 
                   (10, legend_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        output_path = 'level2_menu_analyzed.png'
        cv2.imwrite(output_path, result)
        print(f"   ✅ 保存: {output_path}")
        
        return output_path
    
    def generate_level2_report(self):
        """生成二级菜单报告"""
        print("\n📊 生成二级菜单报告")
        print("-" * 60)
        
        # 分析二级菜单项
        level2_items = self.analyze_level2_items()
        
        # 检测学时文本
        hours_positions = self.detect_hours_text_positions()
        
        report = {
            'image': {
                'path': self.image_path,
                'width': self.image.shape[1],
                'height': self.image.shape[0]
            },
            'level1_buttons': len(self.level1_buttons),
            'level2_regions': [
                {
                    'parent_button': r['parent_button'],
                    'y_start': int(r['y_start']),
                    'y_end': int(r['y_end']),
                    'height': int(r['height']),
                    'estimated_items': r['estimated_items']
                }
                for r in self.level2_regions
            ],
            'level2_items': [
                {
                    'parent_menu': item['parent_menu'],
                    'item_id': item['item_id'],
                    'y': int(item['y']),
                    'height': int(item['height']),
                    'estimated_click_y': int(item['center_y'])
                }
                for item in level2_items
            ],
            'hours_text_positions': hours_positions,
            'statistics': {
                'total_level2_items': len(level2_items),
                'total_hours_detected': len(hours_positions),
                'avg_item_height': int(np.mean([item['height'] for item in level2_items])) if level2_items else 0
            },
            'recommendations': [
                {
                    'type': '二级菜单定位',
                    'suggestion': f'二级菜单平均{np.mean([r["height"] for r in self.level2_regions]):.0f}px高，每个课程项约55px',
                    'confidence': 'high'
                },
                {
                    'type': '学时文本位置',
                    'suggestion': '学时文本通常在X=150-250范围，建议先在此范围搜索',
                    'confidence': 'medium'
                },
                {
                    'type': '点击策略',
                    'suggestion': '先点击一级菜单展开，等待0.5-1秒，然后在二级区域搜索学时文本',
                    'confidence': 'high'
                }
            ]
        }
        
        json_path = 'level2_menu_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 保存: {json_path}")
        
        return report
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("📊 二级菜单分析摘要")
        print("=" * 60)
        
        print(f"\n一级菜单:")
        print(f"  按钮数量: {len(self.level1_buttons)}")
        
        print(f"\n二级菜单:")
        print(f"  区域数量: {len(self.level2_regions)}")
        
        total_items = sum(r['estimated_items'] for r in self.level2_regions)
        print(f"  估计课程总数: {total_items}")
        
        if self.level2_regions:
            avg_height = np.mean([r['height'] for r in self.level2_regions])
            print(f"  平均区域高度: {avg_height:.0f}px")
        
        print("\n关键参数:")
        print("  每个课程项高度: 约55px")
        print("  学时文本X位置: 约150-250")
        print("  点击等待时间: 0.5-1秒")
    
    def run_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("🎓 二级菜单特征分析")
        print("=" * 60)
        
        self.load_image()
        self.detect_level1_buttons()
        self.estimate_level2_regions()
        self.analyze_text_color()
        
        self.create_level2_visualization()
        report = self.generate_level2_report()
        
        self.print_summary()
        
        return report


def main():
    import sys
    
    image_path = 'lists_full.png' if len(sys.argv) < 2 else sys.argv[1]
    
    analyzer = Level2MenuAnalyzer(image_path)
    analyzer.run_analysis()
    
    print("\n" + "=" * 60)
    print("✅ 二级菜单分析完成!")
    print("=" * 60)
    print("\n生成的文件:")
    print("  level2_menu_analyzed.png  - 二级菜单可视化")
    print("  level2_menu_report.json   - 详细分析报告")


if __name__ == '__main__':
    main()


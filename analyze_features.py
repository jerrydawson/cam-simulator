#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片特征分析工具
分析lists_full.png，识别关键特征以提高识别准确率
"""

import cv2
import numpy as np
from PIL import Image
import json
import re


class FeatureAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.gray = None
        self.features = {}
        
    def load_image(self):
        """加载图片"""
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"无法加载图片: {self.image_path}")
        
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        height, width = self.image.shape[:2]
        
        print(f"✅ 图片已加载: {width}x{height}")
        return self.image
    
    def analyze_colors(self):
        """分析颜色特征"""
        print("\n🎨 颜色特征分析")
        print("-" * 60)
        
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 定义颜色范围
        color_ranges = {
            '红色': ([0, 100, 100], [10, 255, 255], [160, 100, 100], [180, 255, 255]),
            '橙色': ([10, 100, 100], [25, 255, 255], None, None),
            '黄色': ([25, 100, 100], [35, 255, 255], None, None),
            '绿色': ([35, 100, 100], [85, 255, 255], None, None),
            '蓝色': ([85, 100, 100], [125, 255, 255], None, None),
            '紫色': ([125, 100, 100], [160, 255, 255], None, None),
        }
        
        color_stats = {}
        
        for color_name, ranges in color_ranges.items():
            if ranges[2] is not None:  # 红色有两个范围
                mask1 = cv2.inRange(hsv, np.array(ranges[0]), np.array(ranges[1]))
                mask2 = cv2.inRange(hsv, np.array(ranges[2]), np.array(ranges[3]))
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                mask = cv2.inRange(hsv, np.array(ranges[0]), np.array(ranges[1]))
            
            # 计算颜色占比
            color_pixels = cv2.countNonZero(mask)
            total_pixels = self.image.shape[0] * self.image.shape[1]
            percentage = (color_pixels / total_pixels) * 100
            
            if percentage > 0.1:  # 只显示占比超过0.1%的颜色
                color_stats[color_name] = {
                    'pixels': int(color_pixels),
                    'percentage': round(percentage, 2)
                }
                print(f"   {color_name}: {color_pixels} 像素 ({percentage:.2f}%)")
                
                # 查找该颜色的轮廓
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                large_contours = [c for c in contours if cv2.contourArea(c) > 200]
                
                if large_contours:
                    print(f"      检测到 {len(large_contours)} 个{color_name}区域")
        
        self.features['colors'] = color_stats
        return color_stats
    
    def analyze_text_regions(self):
        """分析文本区域特征"""
        print("\n📝 文本区域分析")
        print("-" * 60)
        
        # 使用MSER检测文本区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(self.gray)
        
        # 筛选文本区域
        text_regions = []
        for region in regions:
            if len(region) < 10:
                continue
            
            x, y, w, h = cv2.boundingRect(region)
            
            # 文本特征：宽度>高度，高度在合理范围
            aspect_ratio = w / h if h > 0 else 0
            
            if 15 < h < 60 and 2 < aspect_ratio < 20:
                text_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'aspect_ratio': round(aspect_ratio, 2)
                })
        
        print(f"   检测到 {len(text_regions)} 个文本区域")
        
        # 按Y坐标分组（同一行的文本）
        text_regions.sort(key=lambda r: r['y'])
        
        lines = []
        current_line = []
        last_y = -1
        
        for region in text_regions:
            if last_y == -1 or abs(region['y'] - last_y) < 20:
                current_line.append(region)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [region]
            last_y = region['y']
        
        if current_line:
            lines.append(current_line)
        
        print(f"   估计有 {len(lines)} 行文本")
        
        # 分析文本高度分布
        heights = [r['height'] for r in text_regions]
        if heights:
            avg_height = np.mean(heights)
            std_height = np.std(heights)
            print(f"   平均文本高度: {avg_height:.1f}px (±{std_height:.1f})")
        
        self.features['text_regions'] = {
            'total': len(text_regions),
            'lines': len(lines),
            'avg_height': round(float(avg_height), 1) if heights else 0
        }
        
        return text_regions
    
    def detect_buttons_and_icons(self):
        """检测按钮和图标"""
        print("\n🔘 按钮和图标检测")
        print("-" * 60)
        
        # 边缘检测
        edges = cv2.Canny(self.gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 200 or area > 10000:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # 按钮特征：接近正方形或小矩形
            if 0.5 < aspect_ratio < 2.5 and 20 < w < 200 and 20 < h < 80:
                buttons.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(area),
                    'aspect_ratio': round(aspect_ratio, 2)
                })
        
        # 按Y坐标排序
        buttons.sort(key=lambda b: b['y'])
        
        print(f"   检测到 {len(buttons)} 个可能的按钮/图标")
        
        # 按X坐标分组（左侧、中间、右侧）
        width = self.image.shape[1]
        left_buttons = [b for b in buttons if b['x'] < width * 0.3]
        center_buttons = [b for b in buttons if width * 0.3 <= b['x'] < width * 0.7]
        right_buttons = [b for b in buttons if b['x'] >= width * 0.7]
        
        print(f"   左侧: {len(left_buttons)} 个")
        print(f"   中间: {len(center_buttons)} 个")
        print(f"   右侧: {len(right_buttons)} 个")
        
        self.features['buttons'] = {
            'total': len(buttons),
            'left': len(left_buttons),
            'center': len(center_buttons),
            'right': len(right_buttons)
        }
        
        return buttons
    
    def detect_horizontal_lines(self):
        """检测水平分隔线"""
        print("\n📏 水平分隔线检测")
        print("-" * 60)
        
        # 使用形态学操作检测水平线
        width = self.image.shape[1]
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 2, 1))
        detect_horizontal = cv2.morphologyEx(self.gray, cv2.MORPH_CLOSE, horizontal_kernel)
        
        # 边缘检测
        edges = cv2.Canny(detect_horizontal, 50, 150)
        
        # 霍夫变换检测直线
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                                minLineLength=width//3, maxLineGap=20)
        
        horizontal_lines = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 只保留接近水平的线（角度小于5度）
                if abs(y2 - y1) < 5:
                    horizontal_lines.append({
                        'y': int((y1 + y2) / 2),
                        'x1': int(x1),
                        'x2': int(x2),
                        'length': int(abs(x2 - x1))
                    })
        
        # 去重（Y坐标相近的合并）
        horizontal_lines.sort(key=lambda l: l['y'])
        unique_lines = []
        
        for line in horizontal_lines:
            if not unique_lines or abs(line['y'] - unique_lines[-1]['y']) > 10:
                unique_lines.append(line)
        
        print(f"   检测到 {len(unique_lines)} 条水平分隔线")
        
        for i, line in enumerate(unique_lines[:10]):  # 只显示前10条
            print(f"      线{i+1}: Y={line['y']}, 长度={line['length']}px")
        
        self.features['horizontal_lines'] = len(unique_lines)
        
        return unique_lines
    
    def detect_list_structure(self):
        """检测列表结构"""
        print("\n📋 列表结构分析")
        print("-" * 60)
        
        # 基于水平线和文本区域推断列表结构
        lines = self.detect_horizontal_lines()
        
        if len(lines) > 1:
            # 计算行间距
            spacings = []
            for i in range(len(lines) - 1):
                spacing = lines[i + 1]['y'] - lines[i]['y']
                spacings.append(spacing)
            
            if spacings:
                avg_spacing = np.mean(spacings)
                std_spacing = np.std(spacings)
                
                print(f"   平均行间距: {avg_spacing:.1f}px (±{std_spacing:.1f})")
                
                # 估计列表项数量
                height = self.image.shape[0]
                estimated_items = int(height / avg_spacing)
                print(f"   估计列表项数量: {estimated_items}")
                
                self.features['list_structure'] = {
                    'avg_spacing': round(float(avg_spacing), 1),
                    'estimated_items': estimated_items
                }
    
    def detect_hours_pattern(self):
        """检测学时文本模式"""
        print("\n⏰ 学时文本模式分析")
        print("-" * 60)
        
        # 尝试OCR识别（如果可用）
        try:
            import pytesseract
            
            # 对整个图片进行OCR
            text = pytesseract.image_to_string(self.image, lang='chi_sim')
            
            # 查找学时模式
            pattern = r'(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\s*学时'
            matches = re.findall(pattern, text)
            
            if matches:
                print(f"   ✅ 检测到 {len(matches)} 个学时信息")
                
                hours_data = []
                for completed, total in matches:
                    try:
                        c = float(completed)
                        t = float(total)
                        is_incomplete = c < t
                        hours_data.append({
                            'completed': c,
                            'total': t,
                            'incomplete': is_incomplete,
                            'text': f"{c}/{t}学时"
                        })
                    except:
                        pass
                
                # 统计
                incomplete_count = sum(1 for h in hours_data if h['incomplete'])
                complete_count = len(hours_data) - incomplete_count
                
                print(f"   未完成: {incomplete_count} 个")
                print(f"   已完成: {complete_count} 个")
                
                # 显示前几个
                print(f"\n   示例:")
                for i, h in enumerate(hours_data[:5]):
                    status = "❌" if h['incomplete'] else "✅"
                    print(f"      {i+1}. {h['text']} {status}")
                
                self.features['hours_pattern'] = {
                    'total': len(hours_data),
                    'incomplete': incomplete_count,
                    'complete': complete_count
                }
                
                return hours_data
            else:
                print("   ⚠️  未检测到学时信息")
                
        except ImportError:
            print("   ⚠️  pytesseract未安装，跳过OCR分析")
        except Exception as e:
            print(f"   ⚠️  OCR错误: {e}")
        
        return []
    
    def analyze_layout(self):
        """分析整体布局"""
        print("\n🖼️  整体布局分析")
        print("-" * 60)
        
        height, width = self.image.shape[:2]
        
        # 分析垂直密度（每一行的像素变化）
        row_variance = []
        for y in range(0, height, 10):  # 每10行采样
            row = self.gray[y, :]
            variance = np.var(row)
            row_variance.append(variance)
        
        # 找出内容密集区域（方差大的区域）
        threshold = np.mean(row_variance)
        content_regions = []
        in_region = False
        region_start = 0
        
        for i, var in enumerate(row_variance):
            if var > threshold and not in_region:
                in_region = True
                region_start = i * 10
            elif var <= threshold and in_region:
                in_region = False
                content_regions.append((region_start, i * 10))
        
        print(f"   图片尺寸: {width}x{height}")
        print(f"   内容密集区域: {len(content_regions)} 个")
        
        for i, (start, end) in enumerate(content_regions[:5]):
            print(f"      区域{i+1}: Y={start}~{end} (高度: {end-start}px)")
        
        self.features['layout'] = {
            'width': width,
            'height': height,
            'content_regions': len(content_regions)
        }
    
    def create_visualization(self):
        """创建可视化特征图"""
        print("\n🎨 生成特征可视化图...")
        
        result = self.image.copy()
        height, width = result.shape[:2]
        
        # 绘制颜色区域
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 红色区域（一级菜单按钮）
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 3)
                cv2.putText(result, "Level1", (x-60, y+h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # 添加标注
        cv2.putText(result, f"Size: {width}x{height}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 保存
        output_path = 'features_analyzed.png'
        cv2.imwrite(output_path, result)
        print(f"   ✅ 保存: {output_path}")
        
        return output_path
    
    def generate_report(self):
        """生成分析报告"""
        print("\n📊 生成分析报告...")
        
        report = {
            'image': {
                'path': self.image_path,
                'width': int(self.image.shape[1]),
                'height': int(self.image.shape[0])
            },
            'features': self.features,
            'recommendations': self.generate_recommendations()
        }
        
        # 保存JSON
        json_path = 'features_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 保存: {json_path}")
        
        return report
    
    def generate_recommendations(self):
        """生成优化建议"""
        recommendations = []
        
        # 基于颜色特征
        if 'colors' in self.features:
            if '红色' in self.features['colors']:
                recommendations.append({
                    'type': '颜色识别',
                    'suggestion': '使用红色HSV范围([0,100,100]-[10,255,255])识别一级菜单按钮',
                    'confidence': 'high'
                })
        
        # 基于文本区域
        if 'text_regions' in self.features:
            avg_h = self.features['text_regions'].get('avg_height', 0)
            if avg_h > 0:
                recommendations.append({
                    'type': 'OCR优化',
                    'suggestion': f'文本高度约{avg_h}px，建议OCR前预处理：缩放到统一高度30-40px',
                    'confidence': 'medium'
                })
        
        # 基于按钮分布
        if 'buttons' in self.features:
            right_buttons = self.features['buttons'].get('right', 0)
            if right_buttons > 0:
                recommendations.append({
                    'type': '按钮定位',
                    'suggestion': f'右侧有{right_buttons}个按钮，建议优先在图片右侧区域查找菜单按钮',
                    'confidence': 'high'
                })
        
        return recommendations
    
    def run_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("🔍 图片特征分析")
        print("=" * 60)
        
        self.load_image()
        self.analyze_colors()
        self.analyze_text_regions()
        self.detect_buttons_and_icons()
        self.detect_horizontal_lines()
        self.detect_list_structure()
        self.detect_hours_pattern()
        self.analyze_layout()
        
        self.create_visualization()
        report = self.generate_report()
        
        self.print_summary()
        
        return report
    
    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("📊 分析摘要")
        print("=" * 60)
        
        print(f"\n图片信息:")
        print(f"  路径: {self.image_path}")
        print(f"  尺寸: {self.image.shape[1]}x{self.image.shape[0]}")
        
        if self.features:
            print(f"\n检测到的特征:")
            for key, value in self.features.items():
                print(f"  {key}: {value}")
        
        print("\n生成的文件:")
        print("  features_analyzed.png  - 可视化特征图")
        print("  features_report.json   - 详细分析报告")


def main():
    import sys
    
    image_path = 'lists_full.png' if len(sys.argv) < 2 else sys.argv[1]
    
    analyzer = FeatureAnalyzer(image_path)
    analyzer.run_analysis()
    
    print("\n" + "=" * 60)
    print("✅ 分析完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()


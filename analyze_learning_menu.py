#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习菜单分析器（无GUI依赖版本）
分析两级菜单结构和学时信息
"""

import cv2
import numpy as np
import json
import re


class LearningMenuAnalyzer:
    def __init__(self, image_path='lists.png'):
        self.image_path = image_path
        self.image = None
        self.level1_menus = []
        self.level2_items = []
        
    def load_image(self):
        """加载图片"""
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"无法加载图片: {self.image_path}")
        print(f"✅ 图片已加载: {self.image.shape[1]}x{self.image.shape[0]}")
        return self.image
    
    def detect_level1_menus(self):
        """检测一级菜单（红色按钮）"""
        print("\n🔍 检测一级菜单（红色按钮）...")
        
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 红色在HSV中有两个范围
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # 查找红色区域
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
                        'area': area
                    })
        
        # 按Y坐标排序
        buttons.sort(key=lambda b: b['y'])
        
        # 去重（合并相近的按钮）
        unique_buttons = []
        for btn in buttons:
            is_duplicate = False
            for existing in unique_buttons:
                if abs(btn['center_y'] - existing['center_y']) < 50 and \
                   abs(btn['center_x'] - existing['center_x']) < 50:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_buttons.append(btn)
        
        self.level1_menus = unique_buttons
        print(f"   ✅ 找到 {len(self.level1_menus)} 个一级菜单")
        
        for i, menu in enumerate(self.level1_menus):
            print(f"      菜单 {i+1}: 位置({menu['center_x']}, {menu['center_y']})")
        
        return self.level1_menus
    
    def estimate_level2_items(self):
        """估计二级菜单项位置"""
        print("\n📋 分析二级菜单区域...")
        
        level2_regions = []
        
        for i, menu in enumerate(self.level1_menus):
            # 每个一级菜单下方可能有多个二级菜单项
            y_start = menu['y'] + menu['height'] + 10
            
            # 确定区域结束位置
            if i + 1 < len(self.level1_menus):
                y_end = self.level1_menus[i + 1]['y'] - 10
            else:
                # 最后一个菜单到图片底部
                y_end = self.image.shape[0] - 100  # 留出底部空间
            
            region_height = y_end - y_start
            
            if region_height > 30:
                # 估计二级菜单项数量（假设每项约40-50px高）
                est_item_count = max(1, int(region_height / 45))
                
                print(f"\n   一级菜单 {i+1} 的二级菜单区域:")
                print(f"      Y范围: {y_start} ~ {y_end} (高度: {region_height}px)")
                print(f"      估计包含 {est_item_count} 个二级菜单项")
                
                for j in range(est_item_count):
                    # 计算每个二级菜单项的位置
                    item_y = y_start + 25 + j * 45
                    
                    if item_y < y_end - 20:
                        item = {
                            'parent_menu': i + 1,
                            'item_index': j + 1,
                            'x': 50,  # 二级菜单通常在左侧
                            'y': item_y - 15,
                            'width': 500,
                            'height': 30,
                            'center_x': 300,  # 文本中心位置
                            'center_y': item_y,
                            'click_x': 200,  # 学时文本点击位置
                            'click_y': item_y
                        }
                        level2_regions.append(item)
        
        self.level2_items = level2_regions
        print(f"\n   ✅ 总计估计 {len(level2_regions)} 个二级菜单项")
        
        return level2_regions
    
    def detect_text_with_hours(self):
        """检测包含学时信息的文本区域"""
        print("\n📝 检测学时文本区域...")
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # 文本检测（查找包含数字的区域）
        # 使用边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 膨胀以连接文本
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 文本区域特征
            if 80 < w < 400 and 15 < h < 40:
                text_regions.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2
                })
        
        print(f"   找到 {len(text_regions)} 个可能的文本区域")
        return text_regions
    
    def create_visualization(self):
        """创建可视化图"""
        print("\n🎨 生成可视化图...")
        
        result = self.image.copy()
        height, width = result.shape[:2]
        
        # 绘制一级菜单（红色框）
        for i, menu in enumerate(self.level1_menus):
            # 红色粗边框
            cv2.rectangle(result,
                         (menu['x'], menu['y']),
                         (menu['x'] + menu['width'], menu['y'] + menu['height']),
                         (0, 0, 255), 3)
            
            # 蓝色圆点标记中心点
            cv2.circle(result, (menu['center_x'], menu['center_y']), 8, (255, 0, 0), -1)
            
            # 标签
            cv2.putText(result, f"L1-Menu{i+1}", 
                       (menu['x'] - 80, menu['center_y'] + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # 点击提示箭头
            cv2.arrowedLine(result, 
                          (menu['x'] - 100, menu['center_y']),
                          (menu['x'] - 10, menu['center_y']),
                          (0, 0, 255), 2, tipLength=0.3)
        
        # 绘制二级菜单区域（绿色框）
        for i, item in enumerate(self.level2_items):
            # 绿色细边框
            cv2.rectangle(result,
                         (item['x'], item['y']),
                         (item['x'] + item['width'], item['y'] + item['height']),
                         (0, 255, 0), 2)
            
            # 橙色圆点标记点击位置
            cv2.circle(result, (item['click_x'], item['click_y']), 6, (0, 165, 255), -1)
            
            # 标签
            if i % 3 == 0:  # 只标记部分，避免太拥挤
                cv2.putText(result, f"L2-{item['parent_menu']}.{item['item_index']}", 
                           (item['x'] + 10, item['y'] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 添加图例
        legend_x = 10
        legend_y = height - 120
        cv2.rectangle(result, (legend_x - 5, legend_y - 30), 
                     (500, height - 10), (0, 0, 0), -1)
        cv2.rectangle(result, (legend_x - 5, legend_y - 30), 
                     (500, height - 10), (255, 255, 255), 2)
        
        cv2.putText(result, "Legend:", 
                   (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.rectangle(result, (legend_x, legend_y + 10), (legend_x + 30, legend_y + 30), (0, 0, 255), 2)
        cv2.putText(result, "= Level 1 Menu (Red Button) - Click to expand", 
                   (legend_x + 40, legend_y + 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.rectangle(result, (legend_x, legend_y + 40), (legend_x + 30, legend_y + 60), (0, 255, 0), 2)
        cv2.putText(result, "= Level 2 Item (Contains 'x.x/x.x hours')", 
                   (legend_x + 40, legend_y + 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.circle(result, (legend_x + 15, legend_y + 85), 6, (0, 165, 255), -1)
        cv2.putText(result, "= Click point for incomplete items", 
                   (legend_x + 40, legend_y + 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 保存
        output_path = 'learning_menu_structure.png'
        cv2.imwrite(output_path, result)
        print(f"   ✅ 保存成功: {output_path}")
        
        return output_path
    
    def generate_report(self):
        """生成详细报告"""
        report = {
            'image': {
                'path': self.image_path,
                'width': int(self.image.shape[1]),
                'height': int(self.image.shape[0])
            },
            'level1_menus': [
                {
                    'menu_id': i + 1,
                    'x': int(m['x']),
                    'y': int(m['y']),
                    'width': int(m['width']),
                    'height': int(m['height']),
                    'click_x': int(m['center_x']),
                    'click_y': int(m['center_y'])
                }
                for i, m in enumerate(self.level1_menus)
            ],
            'level2_items': [
                {
                    'parent_menu': int(item['parent_menu']),
                    'item_id': int(item['item_index']),
                    'estimated_x': int(item['x']),
                    'estimated_y': int(item['y']),
                    'click_x': int(item['click_x']),
                    'click_y': int(item['click_y']),
                    'note': 'Click L1 menu first to see this item'
                }
                for item in self.level2_items
            ],
            'summary': {
                'total_level1_menus': len(self.level1_menus),
                'total_level2_items_estimated': len(self.level2_items)
            },
            'instructions': {
                'step1': '点击一级菜单（红色按钮）展开二级菜单',
                'step2': '在二级菜单中查找 "x.x/x.x学时" 格式的文本',
                'step3': '如果"/"左右数字不相等，点击该文本开始播放',
                'step4': '重复以上步骤处理所有菜单'
            }
        }
        
        # 保存JSON
        json_path = 'learning_menu_report.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ JSON报告: {json_path}")
        
        return report
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 70)
        print("📊 学习菜单结构分析报告")
        print("=" * 70)
        
        print(f"\n📌 图片: {self.image_path}")
        print(f"   尺寸: {self.image.shape[1]}x{self.image.shape[0]}")
        
        print(f"\n🔴 一级菜单 (红色按钮): {len(self.level1_menus)} 个")
        print("-" * 70)
        for i, menu in enumerate(self.level1_menus):
            print(f"   菜单 {i+1}:")
            print(f"      点击坐标: ({menu['center_x']}, {menu['center_y']}) 👆")
            print(f"      作用: 点击展开二级菜单")
        
        print(f"\n🟢 二级菜单项: 约 {len(self.level2_items)} 个")
        print("-" * 70)
        
        # 按父菜单分组
        by_parent = {}
        for item in self.level2_items:
            parent = item['parent_menu']
            if parent not in by_parent:
                by_parent[parent] = []
            by_parent[parent].append(item)
        
        for parent in sorted(by_parent.keys()):
            items = by_parent[parent]
            print(f"\n   ├─ 一级菜单 {parent} 下的二级项目: {len(items)} 个")
            for item in items[:3]:  # 只显示前3个
                print(f"   │  项目 {parent}.{item['item_index']}: ")
                print(f"   │    估计点击位置: ({item['click_x']}, {item['click_y']})")
            if len(items) > 3:
                print(f"   │  ... 还有 {len(items) - 3} 个项目")
        
        print("\n" + "=" * 70)
        print("📖 使用说明")
        print("=" * 70)
        print("""
操作流程:
  
  1️⃣  点击一级菜单（红色按钮）
      → 二级菜单展开
      
  2️⃣  在二级菜单中查找学时信息
      → 格式: "x.x/x.x学时" (例如: "0.5/2.0学时")
      
  3️⃣  判断是否需要学习
      → 如果左边数字 < 右边数字 (未完成)
      → 点击该文本开始播放视频
      
  4️⃣  重复步骤1-3
      → 遍历所有一级菜单
      → 完成所有未完成的课程

示例:
  "0.0/2.0学时" → 需要点击 ❌ (未开始)
  "1.5/2.0学时" → 需要点击 ❌ (未完成)
  "2.0/2.0学时" → 不需要点击 ✅ (已完成)
""")


def main():
    print("=" * 70)
    print("🎓 在线学习菜单结构分析器")
    print("=" * 70)
    print("\n分析图片中的两级菜单结构:")
    print("  • 一级菜单: 红色按钮")
    print("  • 二级菜单: 包含 'x.x/x.x学时' 的课程项")
    print()
    
    analyzer = LearningMenuAnalyzer('lists.png')
    
    # 加载图片
    analyzer.load_image()
    
    # 检测一级菜单
    analyzer.detect_level1_menus()
    
    # 估计二级菜单
    analyzer.estimate_level2_items()
    
    # 创建可视化
    analyzer.create_visualization()
    
    # 生成报告
    analyzer.generate_report()
    
    # 打印摘要
    analyzer.print_summary()
    
    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)
    print("\n生成的文件:")
    print("  1. learning_menu_structure.png  - 可视化菜单结构")
    print("  2. learning_menu_report.json    - JSON格式报告")
    print("\n查看可视化:")
    print("  xdg-open learning_menu_structure.png")


if __name__ == '__main__':
    main()


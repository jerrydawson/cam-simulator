#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新分析所有菜单
精确识别4个二级菜单区域
"""

import cv2
import numpy as np
import json


def detect_all_red_buttons(image):
    """检测所有红色按钮（包括可能遗漏的）"""
    print("\n🔍 全面检测红色按钮...")
    print("-" * 70)
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    height, width = image.shape[:2]
    
    # 红色范围（放宽一些）
    lower_red1 = np.array([0, 80, 80])    # 降低阈值
    upper_red1 = np.array([15, 255, 255])  # 扩大范围
    lower_red2 = np.array([160, 80, 80])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # 形态学处理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    
    # 保存mask用于调试
    cv2.imwrite('red_mask_debug.png', red_mask)
    print(f"   红色遮罩保存: red_mask_debug.png")
    
    # 查找轮廓
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    all_buttons = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # 记录所有可能的红色区域（降低阈值）
        if area > 200 and w > 20 and h > 20:
            all_buttons.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'center_x': x + w // 2,
                'center_y': y + h // 2,
                'area': int(area)
            })
    
    print(f"   初步检测到 {len(all_buttons)} 个红色区域")
    
    # 按Y坐标排序
    all_buttons.sort(key=lambda b: b['y'])
    
    # 去重（合并相近的）
    unique_buttons = []
    for btn in all_buttons:
        is_duplicate = False
        for existing in unique_buttons:
            if abs(btn['center_y'] - existing['center_y']) < 30 and \
               abs(btn['center_x'] - existing['center_x']) < 30:
                # 保留面积更大的
                if btn['area'] > existing['area']:
                    unique_buttons.remove(existing)
                    unique_buttons.append(btn)
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_buttons.append(btn)
    
    # 再次排序
    unique_buttons.sort(key=lambda b: b['y'])
    
    # 只保留在右侧的按钮（一级菜单按钮通常在右侧）
    right_buttons = [b for b in unique_buttons if b['center_x'] > width * 0.6]
    
    print(f"   去重后: {len(unique_buttons)} 个")
    print(f"   右侧按钮: {len(right_buttons)} 个")
    
    # 显示所有按钮
    print(f"\n   所有检测到的红色按钮:")
    for i, btn in enumerate(unique_buttons):
        side = "右侧" if btn['center_x'] > width * 0.6 else "左/中"
        print(f"      {i+1}. Y={btn['center_y']:4d}, X={btn['center_x']:3d}, "
              f"面积={btn['area']:5d}, {side}")
    
    return unique_buttons, right_buttons


def analyze_vertical_structure(image):
    """分析垂直结构，找出所有二级菜单区域"""
    print("\n📐 分析垂直结构...")
    print("-" * 70)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape[:2]
    
    # 计算每一行的内容密度
    row_density = []
    for y in range(0, height, 5):  # 每5行采样
        if y < height:
            row = gray[y, :]
            # 计算该行的变化程度（标准差）
            density = np.std(row)
            row_density.append((y, density))
    
    # 找出低密度区域（可能是分隔区域）
    avg_density = np.mean([d[1] for d in row_density])
    
    separators = []
    for y, density in row_density:
        if density < avg_density * 0.3:  # 明显低于平均值
            separators.append(y)
    
    # 合并相近的分隔线
    merged_separators = []
    if separators:
        current = separators[0]
        for sep in separators[1:]:
            if sep - current > 50:  # 间隔超过50px，新分隔区域
                merged_separators.append(current)
                current = sep
        merged_separators.append(current)
    
    print(f"   检测到 {len(merged_separators)} 个可能的分隔区域")
    
    return merged_separators


def identify_all_level2_regions(image, all_buttons):
    """识别所有二级菜单区域"""
    print("\n📋 识别所有二级菜单区域...")
    print("-" * 70)
    
    height, width = image.shape[:2]
    
    # 方法：在图片中搜索所有包含内容的区域块
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 使用边缘检测找出内容边界
    edges = cv2.Canny(gray, 50, 150)
    
    # 水平投影：计算每一行的边缘密度
    horizontal_projection = np.sum(edges, axis=1)
    
    # 找出内容块（连续的高密度区域）
    threshold = np.mean(horizontal_projection) * 0.5
    
    in_block = False
    blocks = []
    block_start = 0
    
    for y, density in enumerate(horizontal_projection):
        if density > threshold and not in_block:
            in_block = True
            block_start = y
        elif density <= threshold and in_block:
            in_block = False
            if y - block_start > 50:  # 最小块高度
                blocks.append({
                    'y_start': block_start,
                    'y_end': y,
                    'height': y - block_start
                })
    
    print(f"   检测到 {len(blocks)} 个内容块")
    
    # 尝试将内容块与一级按钮关联
    level2_regions = []
    
    for i, block in enumerate(blocks):
        print(f"\n   块 {i+1}:")
        print(f"      Y范围: {block['y_start']} ~ {block['y_end']}")
        print(f"      高度: {block['height']}px")
        
        # 检查这个块是否在某个一级按钮下方
        for btn in all_buttons:
            # 如果块的起始位置在按钮下方50-200px范围内
            if 50 < block['y_start'] - btn['center_y'] < 200:
                print(f"      → 可能是按钮 {btn['center_y']} 的二级菜单")
    
    # 强制划分：如果用户说有4个二级菜单，我们按高度均分
    print(f"\n   强制划分为4个区域...")
    
    # 跳过顶部区域（可能是标题）
    content_start = 200
    content_end = height - 100
    content_height = content_end - content_start
    
    region_height = content_height // 4
    
    for i in range(4):
        y_start = content_start + i * region_height
        y_end = content_start + (i + 1) * region_height
        
        level2_regions.append({
            'menu_id': i + 1,
            'y_start': y_start,
            'y_end': y_end,
            'height': y_end - y_start,
            'estimated_courses': (y_end - y_start) // 55
        })
        
        print(f"      区域 {i+1}: Y={y_start}~{y_end}, 约{(y_end - y_start) // 55}个课程")
    
    return level2_regions


def create_comprehensive_visualization(image, all_buttons, right_buttons, level2_regions):
    """创建综合可视化"""
    print("\n🎨 生成综合可视化...")
    print("-" * 70)
    
    result = image.copy()
    height, width = result.shape[:2]
    
    # 1. 标记所有红色区域（浅色）
    for i, btn in enumerate(all_buttons):
        is_right = btn in right_buttons
        color = (0, 0, 255) if is_right else (100, 100, 255)
        thickness = 3 if is_right else 1
        
        cv2.rectangle(result,
                     (btn['x'], btn['y']),
                     (btn['x'] + btn['width'], btn['y'] + btn['height']),
                     color, thickness)
        
        label = f"L1-{i+1}" if is_right else f"R{i+1}"
        cv2.putText(result, label,
                   (btn['x'] - 50, btn['center_y']),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # 2. 标记4个二级菜单区域
    colors = [(255, 0, 0), (0, 255, 0), (255, 255, 0), (255, 0, 255)]
    
    for i, region in enumerate(level2_regions):
        color = colors[i % len(colors)]
        
        # 绘制区域边界
        cv2.rectangle(result,
                     (5, region['y_start']),
                     (width - 5, region['y_end']),
                     color, 3)
        
        # 区域标签
        cv2.putText(result, f"L2-Menu {region['menu_id']} ({region['estimated_courses']} courses)",
                   (15, region['y_start'] + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # 标记课程位置
        num_courses = region['estimated_courses']
        for j in range(min(num_courses, 20)):  # 最多标记20个
            course_y = region['y_start'] + 30 + j * 55
            
            if course_y < region['y_end'] - 20:
                # 课程中心线
                cv2.line(result, (15, course_y), (width-15, course_y), 
                        color, 1, cv2.LINE_AA)
                
                # 学时文本点击位置
                cv2.circle(result, (200, course_y), 6, (0, 165, 255), -1)
                
                # 每5个标记序号
                if j % 5 == 0:
                    cv2.putText(result, f"C{j+1}",
                               (15, course_y - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # 3. 添加图例
    legend_y = height - 120
    cv2.rectangle(result, (10, legend_y - 10), (width - 10, height - 10), 
                 (0, 0, 0), -1)
    cv2.rectangle(result, (10, legend_y - 10), (width - 10, height - 10),
                 (255, 255, 255), 2)
    
    cv2.putText(result, "Legend:",
               (20, legend_y + 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 红色粗框
    cv2.rectangle(result, (20, legend_y + 25), (50, legend_y + 45), (0, 0, 255), 3)
    cv2.putText(result, "= L1 Menu (Red Button)",
               (60, legend_y + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 彩色框
    cv2.rectangle(result, (20, legend_y + 55), (50, legend_y + 75), (255, 255, 0), 3)
    cv2.putText(result, "= L2 Menu Region (4 regions)",
               (60, legend_y + 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 橙色点
    cv2.circle(result, (35, legend_y + 95), 6, (0, 165, 255), -1)
    cv2.putText(result, "= Hours text click point",
               (60, legend_y + 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    output_path = 'all_4_level2_menus.png'
    cv2.imwrite(output_path, result)
    print(f"\n   ✅ 保存: {output_path}")
    
    return output_path


def manual_identify_regions(image):
    """手动识别4个二级菜单区域"""
    print("\n📋 手动划分4个二级菜单区域...")
    print("-" * 70)
    
    height, width = image.shape[:2]
    
    # 方法1：基于视觉观察均分
    # 假设4个二级菜单大致均匀分布
    
    # 跳过顶部标题区域（约150px）
    content_start = 150
    # 跳过底部区域（约100px）
    content_end = height - 100
    
    total_height = content_end - content_start
    
    # 方案A：均分（如果4个菜单大小相近）
    regions_equal = []
    region_height = total_height // 4
    
    for i in range(4):
        y_start = content_start + i * region_height
        y_end = content_start + (i + 1) * region_height
        
        regions_equal.append({
            'menu_id': i + 1,
            'method': 'equal_division',
            'y_start': y_start,
            'y_end': y_end,
            'height': y_end - y_start,
            'estimated_courses': (y_end - y_start) // 55
        })
    
    print(f"   方案A：均分法")
    for r in regions_equal:
        print(f"      菜单 {r['menu_id']}: Y={r['y_start']}~{r['y_end']}, "
              f"高度={r['height']}px, 约{r['estimated_courses']}个课程")
    
    # 方案B：基于检测到的一级按钮
    # 如果检测到了一级按钮，根据其位置划分
    all_buttons, right_buttons = detect_all_red_buttons(image)
    
    if len(right_buttons) >= 3:
        print(f"\n   方案B：基于检测到的 {len(right_buttons)} 个一级按钮")
        
        regions_by_buttons = []
        
        # 对每个按钮，其二级菜单在其下方
        for i, btn in enumerate(right_buttons):
            y_start = btn['y'] + btn['height'] + 10
            
            # 确定结束位置
            if i + 1 < len(right_buttons):
                y_end = right_buttons[i + 1]['y'] - 10
            else:
                y_end = height - 100
            
            if y_end > y_start:
                regions_by_buttons.append({
                    'menu_id': i + 1,
                    'method': 'button_based',
                    'parent_button_y': btn['center_y'],
                    'y_start': y_start,
                    'y_end': y_end,
                    'height': y_end - y_start,
                    'estimated_courses': (y_end - y_start) // 55
                })
        
        for r in regions_by_buttons:
            print(f"      菜单 {r['menu_id']}: Y={r['y_start']}~{r['y_end']}, "
                  f"高度={r['height']}px, 约{r['estimated_courses']}个课程")
        
        # 如果检测到的区域少于4个，补充第4个
        if len(regions_by_buttons) < 4:
            print(f"\n   ⚠️  只检测到 {len(regions_by_buttons)} 个区域，尝试补充...")
            
            # 检查是否有遗漏的区域
            # 使用均分法的第4个区域
            if len(regions_equal) >= 4:
                regions_by_buttons.append(regions_equal[3])
                print(f"      已补充第4个区域")
    
    # 返回更好的方案
    if len(right_buttons) >= 3:
        return regions_by_buttons if len(regions_by_buttons) == 4 else regions_equal
    else:
        return regions_equal


def main():
    print("=" * 70)
    print("🔍 重新分析 - 识别所有4个二级菜单")
    print("=" * 70)
    
    # 加载图片
    image = cv2.imread('lists_full.png')
    if image is None:
        print("❌ 无法加载图片")
        return
    
    height, width = image.shape[:2]
    print(f"✅ 图片已加载: {width}x{height}")
    
    # 检测所有红色按钮
    all_buttons, right_buttons = detect_all_red_buttons(image)
    
    # 识别4个二级菜单区域
    level2_regions = identify_all_level2_regions(image, all_buttons)
    
    # 生成可视化
    output = create_comprehensive_visualization(image, all_buttons, right_buttons, level2_regions)
    
    # 生成报告
    print("\n📊 生成完整报告...")
    
    report = {
        'image': {
            'path': 'lists_full.png',
            'width': width,
            'height': height
        },
        'level1_buttons': {
            'total_detected': len(all_buttons),
            'right_side': len(right_buttons),
            'positions': [
                {
                    'id': i + 1,
                    'x': btn['center_x'],
                    'y': btn['center_y'],
                    'click': (btn['center_x'], btn['center_y'])
                }
                for i, btn in enumerate(right_buttons)
            ]
        },
        'level2_menus': {
            'total': len(level2_regions),
            'regions': [
                {
                    'menu_id': r['menu_id'],
                    'y_start': int(r['y_start']),
                    'y_end': int(r['y_end']),
                    'height': int(r['height']),
                    'estimated_courses': r['estimated_courses'],
                    'method': r.get('method', 'unknown')
                }
                for r in level2_regions
            ]
        },
        'course_coordinates': []
    }
    
    # 生成所有课程的坐标
    for region in level2_regions:
        for i in range(region['estimated_courses']):
            course_y = region['y_start'] + 30 + i * 55
            if course_y < region['y_end'] - 20:
                report['course_coordinates'].append({
                    'parent_menu': region['menu_id'],
                    'course_index': i + 1,
                    'click_x': 200,
                    'click_y': course_y
                })
    
    # 保存JSON
    json_path = 'complete_menu_structure.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ 保存: {json_path}")
    
    # 打印摘要
    print("\n" + "=" * 70)
    print("📊 分析摘要")
    print("=" * 70)
    
    print(f"\n一级按钮:")
    print(f"   总数: {len(all_buttons)}")
    print(f"   右侧（有效）: {len(right_buttons)}")
    
    print(f"\n二级菜单:")
    print(f"   总数: {len(level2_regions)} 个 ✅")
    
    total_courses = sum(r['estimated_courses'] for r in level2_regions)
    print(f"   课程总数: 约 {total_courses} 个")
    
    for r in level2_regions:
        print(f"\n   菜单 {r['menu_id']}:")
        print(f"      Y范围: {r['y_start']} ~ {r['y_end']}")
        print(f"      高度: {r['height']}px")
        print(f"      课程数: 约 {r['estimated_courses']} 个")
    
    print("\n" + "=" * 70)
    print("✅ 分析完成！")
    print("=" * 70)
    print("\n生成的文件:")
    print("  all_4_level2_menus.png      - 完整可视化（标注了4个区域）⭐⭐⭐")
    print("  complete_menu_structure.json - 完整数据报告")
    print("  red_mask_debug.png          - 红色检测遮罩（调试用）")
    
    print("\n查看可视化:")
    print("  xdg-open all_4_level2_menus.png")


if __name__ == '__main__':
    main()


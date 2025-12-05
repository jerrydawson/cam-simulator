#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示所有4个二级菜单的28个课程坐标
纯计算版本，不依赖pyautogui
"""

import json


# 4个二级菜单的配置
MENUS = [
    {'id': 1, 'y_start': 200, 'y_end': 639, 'height': 439, 'courses': 7},
    {'id': 2, 'y_start': 639, 'y_end': 1078, 'height': 439, 'courses': 7},
    {'id': 3, 'y_start': 1078, 'y_end': 1517, 'height': 439, 'courses': 7},
    {'id': 4, 'y_start': 1517, 'y_end': 1956, 'height': 439, 'courses': 7},
]

# 学时文本的X位置
HOURS_TEXT_X = 200


def get_course_coordinates(menu_id, course_index):
    """
    计算课程坐标
    
    Args:
        menu_id: 菜单ID (1-4)
        course_index: 课程索引 (0-6)
    
    Returns:
        (x, y): 点击坐标
    """
    menu = MENUS[menu_id - 1]
    y_start = menu['y_start']
    
    # 第一个课程在区域顶部下方30px，然后每个课程间隔55px
    course_y = y_start + 30 + course_index * 55
    
    return (HOURS_TEXT_X, course_y)


def print_all_coordinates():
    """打印所有课程坐标"""
    print("\n" + "="*70)
    print("📍 所有4个二级菜单的28个课程点击坐标")
    print("="*70)
    
    all_coords = []
    
    for menu in MENUS:
        menu_id = menu['id']
        num_courses = menu['courses']
        
        print(f"\n{'─'*70}")
        print(f"🎓 菜单 {menu_id} - Y范围: {menu['y_start']}~{menu['y_end']} ({num_courses}个课程)")
        print(f"{'─'*70}")
        
        menu_coords = []
        
        for i in range(num_courses):
            x, y = get_course_coordinates(menu_id, i)
            menu_coords.append({'x': x, 'y': y})
            all_coords.append({'menu': menu_id, 'course': i+1, 'x': x, 'y': y})
            
            print(f"  课程 {i+1}: ({x:3d}, {y:4d})")
        
        print(f"\n  Python代码格式:")
        print(f"  menu_{menu_id}_courses = [")
        for i, coord in enumerate(menu_coords):
            comma = ',' if i < len(menu_coords) - 1 else ''
            print(f"      ({coord['x']}, {coord['y']}){comma}  # 课程{i+1}")
        print(f"  ]")
    
    # 总计
    print("\n" + "="*70)
    print("📊 统计")
    print("="*70)
    print(f"  二级菜单总数: {len(MENUS)}")
    print(f"  课程总数: {len(all_coords)}")
    print(f"  学时文本X位置: {HOURS_TEXT_X}")
    print(f"  课程高度间隔: 55px")
    print(f"  每个菜单高度: 439px")
    
    return all_coords


def generate_all_python_code():
    """生成完整的Python代码"""
    print("\n" + "="*70)
    print("🐍 完整Python代码")
    print("="*70)
    
    print("\n# 所有28个课程的点击坐标")
    print("ALL_COURSES = [")
    
    for menu in MENUS:
        menu_id = menu['id']
        num_courses = menu['courses']
        
        print(f"    # 菜单 {menu_id}")
        
        for i in range(num_courses):
            x, y = get_course_coordinates(menu_id, i)
            comma = ',' if not (menu_id == 4 and i == num_courses - 1) else ''
            print(f"    ({x}, {y}){comma}")
        
        if menu_id < len(MENUS):
            print()
    
    print("]")
    
    print("\n# 按菜单分组")
    for menu in MENUS:
        menu_id = menu['id']
        num_courses = menu['courses']
        
        print(f"\nMENU_{menu_id}_COURSES = [")
        for i in range(num_courses):
            x, y = get_course_coordinates(menu_id, i)
            comma = ',' if i < num_courses - 1 else ''
            print(f"    ({x}, {y}){comma}  # 课程{i+1}")
        print("]")


def save_to_json():
    """保存为JSON格式"""
    data = {
        'menus': [],
        'all_coordinates': []
    }
    
    for menu in MENUS:
        menu_id = menu['id']
        num_courses = menu['courses']
        
        menu_data = {
            'menu_id': menu_id,
            'y_start': menu['y_start'],
            'y_end': menu['y_end'],
            'height': menu['height'],
            'courses': []
        }
        
        for i in range(num_courses):
            x, y = get_course_coordinates(menu_id, i)
            
            course_data = {
                'course_id': i + 1,
                'click_x': x,
                'click_y': y
            }
            
            menu_data['courses'].append(course_data)
            
            data['all_coordinates'].append({
                'menu': menu_id,
                'course': i + 1,
                'x': x,
                'y': y
            })
        
        data['menus'].append(menu_data)
    
    output_file = 'all_28_courses_coordinates.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存到: {output_file}")


def main():
    """主函数"""
    import sys
    
    # 打印坐标
    coords = print_all_coordinates()
    
    # 生成Python代码
    generate_all_python_code()
    
    # 保存JSON
    save_to_json()
    
    print("\n" + "="*70)
    print("✅ 完成!")
    print("="*70)


if __name__ == '__main__':
    main()


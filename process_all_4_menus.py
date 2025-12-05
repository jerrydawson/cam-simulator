#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理所有4个二级菜单
遍历所有28个课程位置
"""

import pyautogui
import time
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

# 等待时间
CLICK_INTERVAL = 0.3
MOVE_DURATION = 0.2


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


def process_menu(menu, dry_run=False):
    """
    处理一个二级菜单
    
    Args:
        menu: 菜单配置字典
        dry_run: 是否为模拟运行（只打印不点击）
    
    Returns:
        int: 处理的课程数量
    """
    menu_id = menu['id']
    num_courses = menu['courses']
    
    print(f"\n{'='*60}")
    print(f"🎓 菜单 {menu_id} (Y={menu['y_start']}~{menu['y_end']})")
    print(f"{'='*60}")
    
    processed = 0
    
    for i in range(num_courses):
        x, y = get_course_coordinates(menu_id, i)
        
        print(f"  课程 {i+1}/{num_courses}: 点击 ({x:3d}, {y:4d})", end='')
        
        if not dry_run:
            try:
                # 移动鼠标
                pyautogui.moveTo(x, y, duration=MOVE_DURATION)
                
                # 点击
                pyautogui.click()
                
                print(" ✅")
                
                # 等待
                time.sleep(CLICK_INTERVAL)
                
                processed += 1
            except Exception as e:
                print(f" ❌ 错误: {e}")
        else:
            print(" [模拟]")
            processed += 1
    
    print(f"\n  菜单 {menu_id} 完成: {processed}/{num_courses} 个课程")
    
    return processed


def process_all_menus(dry_run=False, start_menu=1, start_course=0):
    """
    处理所有4个二级菜单
    
    Args:
        dry_run: 是否为模拟运行
        start_menu: 从第几个菜单开始 (1-4)
        start_course: 从第几个课程开始 (0-6)
    
    Returns:
        dict: 统计信息
    """
    print("="*60)
    print("🎓 处理所有4个二级菜单")
    print("="*60)
    
    if dry_run:
        print("\n⚠️  模拟运行模式（不会实际点击）\n")
    else:
        print("\n⚠️  实际运行模式（将执行点击操作）")
        print("👉 3秒后开始，请切换到目标窗口...\n")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("\n✅ 开始处理!\n")
    
    total_processed = 0
    total_courses = sum(m['courses'] for m in MENUS)
    
    start_time = time.time()
    
    for menu in MENUS:
        menu_id = menu['id']
        
        # 跳过已处理的菜单
        if menu_id < start_menu:
            print(f"\n⏭️  跳过菜单 {menu_id} (已处理)")
            continue
        
        # 处理该菜单
        processed = process_menu(menu, dry_run=dry_run)
        total_processed += processed
        
        # 菜单间短暂停顿
        if menu_id < len(MENUS):
            time.sleep(0.5)
    
    elapsed_time = time.time() - start_time
    
    # 打印统计
    print("\n" + "="*60)
    print("📊 处理统计")
    print("="*60)
    print(f"  总课程数: {total_courses}")
    print(f"  已处理: {total_processed}")
    print(f"  成功率: {total_processed/total_courses*100:.1f}%")
    print(f"  耗时: {elapsed_time:.1f}秒")
    print(f"  平均每课程: {elapsed_time/total_processed:.2f}秒" if total_processed > 0 else "")
    print("="*60)
    
    return {
        'total': total_courses,
        'processed': total_processed,
        'elapsed_time': elapsed_time,
        'success_rate': total_processed / total_courses if total_courses > 0 else 0
    }


def save_progress(menu_id, course_id):
    """保存进度"""
    progress = {
        'menu': menu_id,
        'course': course_id,
        'timestamp': time.time()
    }
    
    with open('processing_progress.json', 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)


def load_progress():
    """加载进度"""
    try:
        with open('processing_progress.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'menu': 1, 'course': 0}


def print_all_coordinates():
    """打印所有课程坐标"""
    print("\n" + "="*60)
    print("📍 所有28个课程的点击坐标")
    print("="*60)
    
    for menu in MENUS:
        menu_id = menu['id']
        num_courses = menu['courses']
        
        print(f"\n菜单 {menu_id} ({num_courses}个课程):")
        
        for i in range(num_courses):
            x, y = get_course_coordinates(menu_id, i)
            print(f"  课程 {i+1}: ({x:3d}, {y:4d})")


def main():
    """主函数"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == '--coords':
            # 只打印坐标
            print_all_coordinates()
            return
        
        elif mode == '--dry-run':
            # 模拟运行
            process_all_menus(dry_run=True)
            return
        
        elif mode == '--help':
            print("使用方法:")
            print("  python process_all_4_menus.py            # 实际运行")
            print("  python process_all_4_menus.py --dry-run  # 模拟运行")
            print("  python process_all_4_menus.py --coords   # 打印坐标")
            print("  python process_all_4_menus.py --help     # 显示帮助")
            return
    
    # 默认：实际运行
    process_all_menus(dry_run=False)


if __name__ == '__main__':
    main()


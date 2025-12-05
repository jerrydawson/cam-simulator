#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口查找演示
通过窗口标题"课程详情"查找窗口位置
"""

import time

def find_window_method1():
    """方法1：使用pygetwindow（推荐）"""
    print("方法1：使用pygetwindow查找窗口")
    print("-" * 60)
    
    try:
        import pygetwindow as gw
        
        # 查找所有窗口
        all_windows = gw.getAllTitles()
        print(f"系统中共有 {len(all_windows)} 个窗口")
        
        # 查找包含"课程"的窗口
        print("\n包含'课程'的窗口:")
        course_windows = [w for w in all_windows if '课程' in w]
        for i, title in enumerate(course_windows):
            print(f"  {i+1}. {title}")
        
        # 查找"课程详情"窗口
        print("\n查找'课程详情'窗口:")
        windows = gw.getWindowsWithTitle('课程详情')
        
        if windows:
            win = windows[0]
            print(f"✅ 找到窗口!")
            print(f"   标题: {win.title}")
            print(f"   位置: ({win.left}, {win.top})")
            print(f"   尺寸: {win.width}x{win.height}")
            
            # 激活窗口
            try:
                win.activate()
                print(f"✅ 窗口已激活")
            except:
                print(f"⚠️  无法激活窗口（可能需要手动点击）")
            
            return win.left, win.top
        else:
            print("❌ 未找到'课程详情'窗口")
            return None, None
            
    except ImportError:
        print("❌ pygetwindow未安装")
        print("   安装: pip install pygetwindow")
        return None, None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None, None


def find_window_method2():
    """方法2：使用xdotool（Linux）"""
    print("\n方法2：使用xdotool查找窗口（Linux）")
    print("-" * 60)
    
    try:
        import subprocess
        
        # 查找窗口
        result = subprocess.run(
            ['xdotool', 'search', '--name', '课程详情'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            window_id = result.stdout.strip().split('\n')[0]
            print(f"✅ 找到窗口ID: {window_id}")
            
            # 获取窗口位置
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', window_id],
                capture_output=True,
                text=True
            )
            
            print(f"窗口信息:\n{result.stdout}")
            
            # 激活窗口
            subprocess.run(['xdotool', 'windowactivate', window_id])
            print(f"✅ 窗口已激活")
            
            return True
        else:
            print("❌ 未找到窗口")
            return False
            
    except FileNotFoundError:
        print("❌ xdotool未安装")
        print("   安装: sudo apt-get install xdotool")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def find_window_method3():
    """方法3：列出所有窗口让用户选择"""
    print("\n方法3：列出所有窗口")
    print("-" * 60)
    
    try:
        import pygetwindow as gw
        
        all_windows = gw.getAllTitles()
        
        # 过滤空标题
        valid_windows = [w for w in all_windows if w.strip()]
        
        print(f"系统中的窗口 (共{len(valid_windows)}个):")
        print()
        
        for i, title in enumerate(valid_windows[:20]):  # 只显示前20个
            print(f"  {i+1:2d}. {title}")
        
        if len(valid_windows) > 20:
            print(f"  ... 还有 {len(valid_windows)-20} 个窗口")
        
        return True
        
    except ImportError:
        print("❌ 需要安装pygetwindow")
        return False


def main():
    print("=" * 60)
    print("窗口查找工具")
    print("=" * 60)
    print()
    
    # 方法1：pygetwindow
    x, y = find_window_method1()
    
    if x is not None:
        print("\n" + "=" * 60)
        print("✅ 成功找到窗口！")
        print(f"窗口左上角坐标: ({x}, {y})")
        print("=" * 60)
        
        # 测试点击
        import pyautogui
        
        choice = input("\n是否测试在窗口上移动鼠标? (y/n): ")
        if choice.lower() == 'y':
            print("\n将鼠标移动到窗口左上角...")
            pyautogui.moveTo(x, y, duration=1)
            time.sleep(0.5)
            
            print("移动到窗口中心...")
            pyautogui.moveTo(x + 400, y + 300, duration=1)
            
            print("✅ 测试完成")
    else:
        # 尝试其他方法
        print("\n尝试其他方法...")
        
        # Linux方法
        find_window_method2()
        
        # 列出所有窗口
        find_window_method3()
        
        print("\n提示:")
        print("  1. 确保'课程详情'窗口已打开")
        print("  2. 窗口标题必须完全匹配")
        print("  3. 安装pygetwindow: pip install pygetwindow")


if __name__ == '__main__':
    main()


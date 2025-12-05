@echo off
chcp 65001 >nul
echo ========================================
echo Windows 虚拟摄像头安装脚本
echo ========================================
echo.

echo [1/3] 检查 Python 安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.7 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

echo [2/3] 检查 OBS Studio...
echo 请确认已安装 OBS Studio
echo 如果还未安装，请访问: https://obsproject.com/download
echo.
set /p continue="已安装 OBS Studio? (Y/N): "
if /i "%continue%" neq "Y" (
    echo 请先安装 OBS Studio，然后重新运行此脚本
    pause
    exit /b 1
)
echo.

echo [3/3] 安装 Python 依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo   命令行版本: python virtual_camera.py video.mp4
echo   图形界面版本: python virtual_camera_gui.py
echo.
echo 示例:
echo   python virtual_camera.py demo.mp4 --width 1280 --height 720 --fps 30
echo.
pause


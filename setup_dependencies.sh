#!/bin/bash
# 自动安装所有依赖

echo "========================================"
echo "自动学习机器人 - 依赖安装脚本"
echo "========================================"
echo

# 检查Python
echo "1. 检查Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python3未安装"
    exit 1
fi

echo

# 安装Python依赖
echo "2. 安装Python依赖..."
pip3 install --upgrade pip

echo "   安装基础库..."
pip3 install pyautogui pillow opencv-python numpy

echo "   安装OCR库..."
pip3 install pytesseract

echo "   安装窗口管理库..."
pip3 install pygetwindow

echo

# 安装系统依赖
echo "3. 安装系统依赖..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   检测到Linux系统"
    
    # 检查包管理器
    if command -v apt-get &> /dev/null; then
        echo "   使用apt-get安装..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim xdotool
        
    elif command -v yum &> /dev/null; then
        echo "   使用yum安装..."
        sudo yum install -y tesseract tesseract-langpack-chi-sim
        
    else
        echo "   ⚠️  未知的包管理器，请手动安装tesseract-ocr"
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   检测到macOS系统"
    
    if command -v brew &> /dev/null; then
        echo "   使用brew安装..."
        brew install tesseract tesseract-lang
    else
        echo "   ❌ Homebrew未安装"
        echo "   请访问: https://brew.sh"
    fi
    
else
    echo "   ⚠️  未知操作系统: $OSTYPE"
fi

echo

# 验证安装
echo "4. 验证安装..."

echo -n "   Python依赖..."
python3 -c "import pyautogui, cv2, pytesseract, PIL" 2>/dev/null && echo "✅" || echo "❌"

echo -n "   窗口库..."
python3 -c "import pygetwindow" 2>/dev/null && echo "✅" || echo "⚠️  (可选)"

echo -n "   Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ $(tesseract --version 2>&1 | head -n1)"
else
    echo "❌"
fi

echo -n "   中文语言包..."
tesseract --list-langs 2>/dev/null | grep -q "chi_sim" && echo "✅" || echo "❌"

echo

# 完成
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "测试安装:"
echo "  python3 find_window_demo.py"
echo
echo "运行机器人:"
echo "  python3 auto_learning_bot.py --test"
echo


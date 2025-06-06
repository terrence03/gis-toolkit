#!/bin/bash

# GIS Toolkit 啟動腳本

echo "🚀 GIS Toolkit 啟動腳本"
echo "========================="
echo ""

# 檢查Python環境
echo "🔍 檢查Python環境..."
if ! command -v python &> /dev/null; then
    echo "❌ Python未安裝，請先安裝Python 3.8+。"
    exit 1
fi

python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python版本: $python_version"

# 安裝依賴（如果需要）
echo ""
echo "📦 檢查依賴套件..."
pip install -r requirements.txt --quiet
echo "✅ 依賴套件檢查完成"

# 測試核心功能
echo ""
echo "🧪 測試核心功能..."
python -c "
from src.graph import Graph, ChoroplethParams, Hist2DParams, DotParams, BubbleParams
print('✅ 核心模組載入成功')
"

if [ $? -ne 0 ]; then
    echo "❌ 核心功能測試失敗"
    exit 1
fi

echo ""
echo "🌐 啟動FastAPI服務器..."
echo "   服務器將在 http://localhost:5010 啟動"
echo "   按 Ctrl+C 停止服務器"
echo ""
echo "📚 可用的URL："
echo "   首頁: http://localhost:5010/"
echo "   API文檔: http://localhost:5010/docs"
echo "   邊界圖: http://localhost:5010/boundary"
echo ""

# 啟動服務器
python app.py

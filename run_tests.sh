#!/bin/bash

# 測試運行腳本

set -e

echo "======================================"
echo "Stock Data System - 測試運行器"
echo "======================================"
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 錯誤: 找不到虛擬環境${NC}"
    echo "請先運行: python3 -m venv venv"
    exit 1
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 檢查測試依賴
echo "📦 檢查測試依賴..."
if ! python -c "import pytest" 2>/dev/null; then
    echo "📥 安裝測試依賴..."
    pip install -r requirements-test.txt
fi

echo ""
echo "請選擇測試類型:"
echo "1) 運行所有測試"
echo "2) 僅運行單元測試"
echo "3) 僅運行集成測試"
echo "4) 運行特定測試文件"
echo "5) 運行特定測試函數"
echo "6) 查看測試覆蓋率"
echo "7) 快速測試（跳過慢速測試）"
echo ""
read -p "請輸入選項 [1-7]: " choice

case $choice in
    1)
        echo -e "${GREEN}✓ 運行所有測試...${NC}"
        pytest -v
        ;;
    2)
        echo -e "${GREEN}✓ 運行單元測試...${NC}"
        pytest -v -m unit
        ;;
    3)
        echo -e "${GREEN}✓ 運行集成測試...${NC}"
        pytest -v -m integration
        ;;
    4)
        read -p "請輸入測試文件路徑 (例如: tests/unit/test_config_manager.py): " test_file
        echo -e "${GREEN}✓ 運行 $test_file${NC}"
        pytest -v "$test_file"
        ;;
    5)
        read -p "請輸入測試函數名 (例如: tests/unit/test_config_manager.py::TestConfigManager::test_load_config_success): " test_func
        echo -e "${GREEN}✓ 運行 $test_func${NC}"
        pytest -v "$test_func"
        ;;
    6)
        echo -e "${GREEN}✓ 運行測試並生成覆蓋率報告...${NC}"
        pytest --cov=src --cov-report=html --cov-report=term
        echo ""
        echo "📊 覆蓋率報告已生成: htmlcov/index.html"
        # 在 macOS 上自動打開
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open htmlcov/index.html
        fi
        ;;
    7)
        echo -e "${GREEN}✓ 運行快速測試（跳過慢速測試）...${NC}"
        pytest -v -m "not slow"
        ;;
    *)
        echo -e "${RED}❌ 無效選項${NC}"
        exit 1
        ;;
esac

# 檢查測試結果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "✅ 所有測試通過！"
    echo "========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================"
    echo "❌ 測試失敗"
    echo "========================================${NC}"
    exit 1
fi

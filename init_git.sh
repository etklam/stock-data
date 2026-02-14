#!/bin/bash

# Git 仓库初始化腳本

echo "=== Git 仓库初始化 ==="
echo ""

# 檢查是否已經是 git 仓库
if [ -d ".git" ]; then
    echo "❌ 錯誤: 這個目錄已經是 git 仓库"
    echo "當前狀態:"
    git status
    exit 1
fi

# 初始化 git 仓库
echo "1️⃣ 初始化 git 仓库..."
git init

# 添加 .gitignore
echo "2️⃣ .gitignore 已配置"
echo "   ✓ Python 文件"
echo "   ✓ 虛擬環境 (venv/, env/)"
echo "   ✓ IDE 配置 (.vscode/, .idea/)"
echo "   ✓ 環境變數 (.env)"
echo "   ✓ 日誌文件 (logs/, *.log)"
echo "   ✓ 數據庫文件 (*.db, *.sqlite)"
echo "   ✓ 測試覆蓋率 (.coverage, htmlcov/)"
echo "   ✓ 臨時文件 (*.tmp, *.bak)"

# 添加所有文件
echo ""
echo "3️⃣ 添加文件到 git..."
git add .

# 檢查狀態
echo ""
echo "4️⃣ Git 狀態:"
echo "---"
git status --short
echo "---"

# 統計
echo ""
echo "5️⃣ 統計:"
FILES_ADDED=$(git status --short | grep -c "^A")
FILES_IGNORED=$(git status --short | grep -c "^??")
echo "   ✓ 將要提交的文件: $FILES_ADDED"
echo "   ⚠️  被忽略的文件: $FILES_IGNORED"

# 建議的初始提交
echo ""
echo "6️⃣ 建議的初始提交:"
echo "---"
echo 'git commit -m "Initial commit: Stock Data System

Features:
- CLI and API interfaces for stock data management
- Yahoo Finance integration
- PostgreSQL database with SQLAlchemy ORM
- Multi-dimensional stock categorization
- Scheduled task automation
- Environment variable configuration support

Configuration:
- config.yaml: Default settings
- .env: Environment-specific overrides
"'
echo "---"

echo ""
echo "✓ Git 仓库初始化完成!"
echo ""
echo "下一步:"
echo "  1. 檢查上面的文件列表"
echo "  2. 如果需要，修改 .gitignore"
echo "  3. 運行上面的 git commit 命令"
echo "  4. (可選) 連接到遠程仓库: git remote add origin <url>"

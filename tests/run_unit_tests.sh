#!/bin/bash

# 隔離環境變數運行單元測試

# 清除環境變數
unset DATABASE_HOST
unset DATABASE_PORT
unset DATABASE_NAME
unset DATABASE_USER
unset DATABASE_PASSWORD
unset API_HOST
unset API_PORT

echo "🔒 已隔離環境變數，運行測試..."
echo ""

# 運行測試
pytest "$@"

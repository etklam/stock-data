#!/usr/bin/env python3
"""
Script to run the Stock Data API server
DEPRECATED: 請使用 'python main.py api' 替代此腳本
此腳本僅為向後相容性保留，未來版本可能移除
"""

import sys
import warnings
from pathlib import Path

# 發出棄用警告
warnings.warn(
    "run_api.py 已棄用，請使用 'python main.py api' 替代。"
    "此腳本僅為向後相容性保留，未來版本可能移除。",
    DeprecationWarning,
    stacklevel=2
)

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 導入並運行 main.py 的 API 功能
if __name__ == '__main__':
    # 重新構建參數列表，模擬 'python main.py api' 命令
    sys.argv = [sys.argv[0], 'api'] + sys.argv[1:]
    
    # 導入並運行 main.py
    import main
    main.main()

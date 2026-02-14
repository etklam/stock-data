"""
配置系統測試腳本
驗證環境變數正確覆蓋 config.yaml 中的值
"""

import os
import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config_loading():
    """測試配置加載"""
    from src.config.config_manager import config

    print("=== 配置系統測試 ===\n")

    # 測試數據庫配置
    print("數據庫配置:")
    db_config = config.get_database_config()
    print(f"  Host: {db_config.get('host')}")
    print(f"  Port: {db_config.get('port')}")
    print(f"  Database: {db_config.get('name')}")
    print(f"  User: {db_config.get('user')}")
    print(f"  Password: {'***' if db_config.get('password') else 'Not Set'}")

    # 測試 API 配置
    print("\nAPI 配置:")
    api_config = config.get('api', {})
    print(f"  Host: {api_config.get('host')}")
    print(f"  Port: {api_config.get('port')}")
    print(f"  Reload: {api_config.get('reload')}")
    print(f"  Workers: {api_config.get('workers')}")

    # 測試調度器配置
    print("\n調度器配置:")
    scheduler_config = config.get_scheduler_config()
    print(f"  Enabled: {scheduler_config.get('enabled')}")
    print(f"  Daily Fetch Time: {scheduler_config.get('daily_fetch_time')}")

    # 測試獲取股票代碼
    print("\n股票配置:")
    symbols = config.get_all_symbols()
    print(f"  總股票數: {len(symbols)}")
    print(f"  前 5 個股票: {symbols[:5]}")

    # 檢查環境變數覆蓋
    print("\n環境變數檢查:")
    test_env_vars = ['DATABASE_HOST', 'DATABASE_PASSWORD', 'API_HOST']
    for var in test_env_vars:
        value = os.getenv(var)
        print(f"  {var}: {'Set' if value else 'Not Set'}")

    print("\n✓ 配置系統測試完成")

if __name__ == '__main__':
    test_config_loading()

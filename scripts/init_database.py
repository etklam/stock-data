"""
數據庫初始化腳本
"""

import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.database.models import Base

logger = get_logger(__name__)


def init_database():
    """初始化數據庫"""
    try:
        logger.info("開始初始化數據庫...")
        
        # 設置日誌
        setup_logging()
        
        # 測試數據庫連接
        if not db_manager.test_connection():
            raise Exception("數據庫連接失敗")
        
        # 初始化數據庫引擎
        db_manager.initialize_engine()
        
        # 創建所有表
        db_manager.create_tables()
        
        # 插入初始配置
        with db_manager.session_scope() as session:
            from src.database.services import SystemConfigService
            
            # 插入系統配置
            configs = [
                ('last_historical_fetch', '', '最後一次歷史數據獲取時間'),
                ('system_initialized', 'true', '系統是否已初始化'),
                ('data_version', '1.0.0', '數據版本'),
                ('categories_initialized', 'false', '分類是否已初始化'),
            ]
            
            for key, value, description in configs:
                SystemConfigService.set_config(session, key, value, description)
        
        logger.info("數據庫初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"數據庫初始化失敗: {e}")
        return False
    finally:
        db_manager.close()


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
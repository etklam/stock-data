"""
股票分類初始化腳本
"""

import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.data_fetcher.data_service import DataFetchService

logger = get_logger(__name__)


def init_categories():
    """初始化股票分類"""
    try:
        logger.info("開始初始化股票分類...")
        
        # 設置日誌
        setup_logging()
        
        # 測試數據庫連接
        if not db_manager.test_connection():
            raise Exception("數據庫連接失敗")
        
        # 初始化數據庫引擎
        db_manager.initialize_engine()
        
        # 創建所有表（包括新的分類表）
        db_manager.create_tables()
        
        # 初始化分類
        data_service = DataFetchService()
        success = data_service.initialize_categories_from_config()
        
        if success:
            logger.info("股票分類初始化完成")
            
            # 顯示初始化結果
            categories = data_service.get_all_categories_with_stocks()
            for category_type, category_dict in categories.items():
                logger.info(f"分類類型: {category_type}")
                for category_name, stocks in category_dict.items():
                    logger.info(f"  {category_name}: {len(stocks)} 隻股票")
                    for stock in stocks[:5]:  # 只顯示前5個
                        logger.info(f"    - {stock}")
                    if len(stocks) > 5:
                        logger.info(f"    ... 還有 {len(stocks) - 5} 隻股票")
        else:
            logger.error("股票分類初始化失敗")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"股票分類初始化失敗: {e}")
        return False
    finally:
        db_manager.close()


if __name__ == '__main__':
    success = init_categories()
    sys.exit(0 if success else 1)
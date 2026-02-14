"""
股票分類功能演示腳本
"""

import sys
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.database.services import StockCategoryService, StockCategoryMappingService, StockPriceService
from src.data_fetcher.data_service import DataFetchService

logger = get_logger(__name__)


def demo_categories():
    """演示股票分類功能"""
    try:
        logger.info("開始演示股票分類功能...")
        
        # 設置日誌
        setup_logging()
        
        # 測試數據庫連接
        if not db_manager.test_connection():
            raise Exception("數據庫連接失敗")
        
        # 初始化數據庫引擎
        db_manager.initialize_engine()
        
        # 初始化分類
        data_service = DataFetchService()
        data_service.initialize_categories_from_config()
        
        with db_manager.session_scope() as session:
            # 1. 顯示所有分類
            logger.info("=== 所有分類 ===")
            all_categories = StockCategoryService.get_all_categories(session)
            for category in all_categories:
                logger.info(f"分類: {category.name} (類型: {category.type})")
            
            # 2. 顯示按類型分組的分類
            logger.info("\n=== 按類型分組的分類 ===")
            enabled_types = config.get_enabled_category_types()
            for category_type in enabled_types:
                logger.info(f"\n分類類型: {category_type}")
                categories = StockCategoryService.get_categories_by_type(session, category_type)
                for category in categories:
                    stocks = StockCategoryMappingService.get_stocks_by_category(session, category.id)
                    logger.info(f"  {category.name}: {len(stocks)} 隻股票")
                    for stock in stocks[:3]:  # 只顯示前3個
                        logger.info(f"    - {stock}")
                    if len(stocks) > 3:
                        logger.info(f"    ... 還有 {len(stocks) - 3} 隻股票")
            
            # 3. 顯示特定股票的分類
            logger.info("\n=== 特定股票的分類 ===")
            sample_symbols = ['AAPL', 'MSFT', '2330.TW']
            for symbol in sample_symbols:
                categories = StockCategoryMappingService.get_stock_categories(session, symbol)
                primary_category = StockCategoryMappingService.get_primary_category(session, symbol)
                
                logger.info(f"\n股票: {symbol}")
                if primary_category:
                    logger.info(f"  主要分類: {primary_category.name} ({primary_category.type})")
                logger.info(f"  所有分類:")
                for category in categories:
                    is_primary = " (主要)" if category.id == primary_category.id else ""
                    logger.info(f"    - {category.name} ({category.type}){is_primary}")
            
            # 4. 演示按分類獲取股票
            logger.info("\n=== 按分類獲取股票 ===")
            category_type = 'industry'
            category_name = '科技業'
            
            # 獲取科技業分類
            tech_category = session.query(StockCategory).filter(
                StockCategory.name == category_name,
                StockCategory.type == category_type
            ).first()
            
            if tech_category:
                tech_stocks = StockCategoryMappingService.get_stocks_by_category(session, tech_category.id)
                logger.info(f"{category_name} 分類下的股票:")
                for stock in tech_stocks:
                    # 獲取最新價格
                    latest_price = StockPriceService.get_latest_price(session, stock)
                    price_info = f" (最新價格: ${latest_price.close_price:.2f})" if latest_price else " (無價格數據)"
                    logger.info(f"  - {stock}{price_info}")
            
            # 5. 演示從配置獲取分類股票
            logger.info("\n=== 從配置獲取分類股票 ===")
            for category_type in enabled_types:
                stocks_by_category = StockCategoryMappingService.get_stocks_by_category_type(session, category_type)
                logger.info(f"\n{category_type} 分類:")
                for category_name, stocks in stocks_by_category.items():
                    logger.info(f"  {category_name}: {len(stocks)} 隻股票")
        
        logger.info("\n股票分類功能演示完成")
        return True
        
    except Exception as e:
        logger.error(f"股票分類功能演示失敗: {e}")
        return False
    finally:
        db_manager.close()


if __name__ == '__main__':
    success = demo_categories()
    sys.exit(0 if success else 1)
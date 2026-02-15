#!/usr/bin/env python3
"""
獲取AAPL過去1年股價並儲存到資料庫的腳本
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加 src 目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.data_fetcher.data_service import DataFetchService
from src.services.stock_service import StockService

logger = get_logger(__name__)


def main():
    """主函數"""
    try:
        # 設置日誌
        setup_logging()
        logger.info("開始獲取AAPL股價數據...")
        
        # 初始化系統
        if not db_manager.test_connection():
            raise Exception("數據庫連接失敗")
        
        db_manager.initialize_engine()
        db_manager.create_tables()
        
        # 創建數據獲取服務
        data_service = DataFetchService()
        
        # 計算過去1年的日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"獲取AAPL從 {start_date_str} 到 {end_date_str} 的股價數據")
        
        # 首先獲取並儲存AAPL的基本信息
        logger.info("獲取AAPL基本信息...")
        stock_info_success = data_service.fetch_and_store_stock_info('AAPL')
        if not stock_info_success:
            logger.error("獲取AAPL基本信息失敗")
            return False
        
        # 獲取並儲存歷史價格數據
        logger.info("獲取AAPL歷史價格數據...")
        success, count = data_service.fetch_and_store_historical_data(
            'AAPL', 
            start_date=start_date_str, 
            end_date=end_date_str
        )
        
        if success:
            logger.info(f"AAPL股價數據獲取成功，共 {count} 條記錄")
            
            # 驗證數據是否成功儲存
            with db_manager.session_scope() as session:
                stock = StockService().get_stock_by_symbol(session, 'AAPL')
                if stock:
                    logger.info(f"AAPL股票信息已儲存: {stock.name} ({stock.symbol})")
                else:
                    logger.warning("未找到AAPL股票信息")
                
                # 獲取最新價格進行驗證
                from src.services.price_service import PriceService
                price_service = PriceService()
                latest_price = price_service.get_latest_price(session, 'AAPL')
                if latest_price:
                    logger.info(f"最新價格已儲存: 日期={latest_price.date}, 收盤價={latest_price.close_price}")
                else:
                    logger.warning("未找到AAPL價格數據")
            
            return True
        else:
            logger.error("AAPL股價數據獲取失敗")
            return False
            
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
        return False
    finally:
        # 關閉數據庫連接
        db_manager.close()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
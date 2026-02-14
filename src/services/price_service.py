"""
股票價格服務
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
import logging

from ..database.repositories.price_repository import PriceRepository

logger = logging.getLogger(__name__)


class PriceService:
    """股票價格服務"""
    
    def __init__(self):
        """初始化價格服務"""
        self.price_repository = PriceRepository()
    
    def save_stock_prices(self, session: Session, symbol: str, price_data: List[Dict[str, Any]]) -> int:
        """
        保存股票價格數據
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            price_data: 價格數據列表
            
        Returns:
            int: 保存的記錄數
        """
        try:
            saved_count = 0
            
            for data in price_data:
                # 檢查是否已存在相同日期的數據
                existing_price = self.price_repository.get_by_symbol_and_date(
                    session, symbol, data['date']
                )
                
                if existing_price:
                    # 更新現有記錄
                    self.price_repository.update(session, existing_price, **data)
                    logger.debug(f"更新股票價格: {symbol} {data['date']}")
                else:
                    # 創建新記錄
                    self.price_repository.create(session, symbol=symbol, **data)
                    logger.debug(f"創建股票價格: {symbol} {data['date']}")
                
                saved_count += 1
            
            return saved_count
        except Exception as e:
            logger.error(f"保存股票價格數據失敗: {e}")
            return 0
    
    def get_latest_price(self, session: Session, symbol: str) -> Optional[object]:
        """
        獲取股票最新價格
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            價格對象或 None
        """
        try:
            return self.price_repository.get_latest_by_symbol(session, symbol)
        except Exception as e:
            logger.error(f"獲取股票最新價格失敗: {e}")
            return None
    
    def get_prices_by_date_range(
        self, 
        session: Session, 
        symbol: str, 
        start_date: date, 
        end_date: date
    ) -> List[object]:
        """
        獲取指定日期範圍的價格數據
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            價格列表
        """
        try:
            return self.price_repository.get_by_symbol_and_date_range(
                session, symbol, start_date, end_date
            )
        except Exception as e:
            logger.error(f"獲取指定日期範圍的價格數據失敗: {e}")
            return []
    
    def get_prices_by_symbols(
        self, 
        session: Session, 
        symbols: List[str], 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[object]:
        """
        獲取多個股票的價格數據
        
        Args:
            session: 數據庫會話
            symbols: 股票代碼列表
            start_date: 開始日期（可選）
            end_date: 結束日期（可選）
            
        Returns:
            價格列表
        """
        try:
            return self.price_repository.get_by_symbols(
                session, symbols, start_date, end_date
            )
        except Exception as e:
            logger.error(f"獲取多個股票的價格數據失敗: {e}")
            return []
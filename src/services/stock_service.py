"""
股票信息服務
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from ..database.repositories.stock_repository import StockRepository

logger = logging.getLogger(__name__)


class StockService:
    """股票信息服務"""
    
    def __init__(self) -> None:
        """初始化股票服務"""
        self.stock_repository = StockRepository()
    
    def create_or_update_stock(self, session: Session, symbol: str, **kwargs) -> bool:
        """
        創建或更新股票信息
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            **kwargs: 其他股票信息
            
        Returns:
            bool: 操作是否成功
        """
        try:
            stock = self.stock_repository.get_by_symbol(session, symbol)
            
            if stock:
                # 更新現有股票信息
                for key, value in kwargs.items():
                    if hasattr(stock, key):
                        setattr(stock, key, value)
                stock.updated_at = datetime.utcnow()
                logger.info(f"更新股票信息: {symbol}")
            else:
                # 創建新股票記錄
                stock = self.stock_repository.create(session, symbol=symbol, **kwargs)
                logger.info(f"創建股票信息: {symbol}")
            
            return True
        except Exception as e:
            logger.error(f"創建或更新股票信息失敗: {e}")
            return False
    
    def get_stock_by_symbol(self, session: Session, symbol: str) -> Optional[object]:
        """
        根據股票代碼獲取股票信息
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            股票對象或 None
        """
        try:
            return self.stock_repository.get_by_symbol(session, symbol)
        except Exception as e:
            logger.error(f"獲取股票信息失敗: {e}")
            return None
    
    def get_all_active_stocks(self, session: Session) -> List[object]:
        """
        獲取所有啟用的股票
        
        Args:
            session: 數據庫會話
            
        Returns:
            股票列表
        """
        try:
            return self.stock_repository.get_all_active(session)
        except Exception as e:
            logger.error(f"獲取所有啟用股票失敗: {e}")
            return []
    
    def get_stocks_by_exchange(self, session: Session, exchange: str) -> List[object]:
        """
        根據交易所獲取股票列表
        
        Args:
            session: 數據庫會話
            exchange: 交易所
            
        Returns:
            股票列表
        """
        try:
            return self.stock_repository.get_by_exchange(session, exchange)
        except Exception as e:
            logger.error(f"根據交易所獲取股票列表失敗: {e}")
            return []
"""
股票數據倉儲
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models import Stock


class StockRepository:
    """股票數據倉儲"""
    
    def create(self, session: Session, **kwargs) -> Stock:
        """
        創建股票記錄
        
        Args:
            session: 數據庫會話
            **kwargs: 股票信息
            
        Returns:
            Stock 對象
        """
        stock = Stock(**kwargs)
        session.add(stock)
        session.flush()
        return stock
    
    def get_by_symbol(self, session: Session, symbol: str) -> Optional[Stock]:
        """
        根據股票代碼獲取股票信息
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            Stock 對象或 None
        """
        return session.query(Stock).filter(Stock.symbol == symbol).first()
    
    def get_all_active(self, session: Session) -> List[Stock]:
        """
        獲取所有啟用的股票
        
        Args:
            session: 數據庫會話
            
        Returns:
            股票列表
        """
        return session.query(Stock).filter(Stock.is_active == True).all()
    
    def get_by_exchange(self, session: Session, exchange: str) -> List[Stock]:
        """
        根據交易所獲取股票列表
        
        Args:
            session: 數據庫會話
            exchange: 交易所
            
        Returns:
            股票列表
        """
        return session.query(Stock).filter(
            and_(Stock.exchange == exchange, Stock.is_active == True)
        ).all()
    
    def update(self, session: Session, stock: Stock, **kwargs) -> Stock:
        """
        更新股票信息
        
        Args:
            session: 數據庫會話
            stock: 股票對象
            **kwargs: 更新的字段
            
        Returns:
            更新後的 Stock 對象
        """
        for key, value in kwargs.items():
            if hasattr(stock, key):
                setattr(stock, key, value)
        session.flush()
        return stock
    
    def delete(self, session: Session, stock: Stock) -> bool:
        """
        刪除股票記錄
        
        Args:
            session: 數據庫會話
            stock: 股票對象
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            session.delete(stock)
            session.flush()
            return True
        except Exception:
            return False
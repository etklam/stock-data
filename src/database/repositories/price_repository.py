"""
股票價格數據倉儲
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from ..models import StockPrice


class PriceRepository:
    """股票價格數據倉儲"""
    
    def create(self, session: Session, **kwargs) -> StockPrice:
        """
        創建價格記錄
        
        Args:
            session: 數據庫會話
            **kwargs: 價格信息
            
        Returns:
            StockPrice 對象
        """
        price = StockPrice(**kwargs)
        session.add(price)
        session.flush()
        return price
    
    def get_by_symbol_and_date(self, session: Session, symbol: str, price_date) -> Optional[StockPrice]:
        """
        根據股票代碼和日期獲取價格記錄
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            price_date: 價格日期 (date 或 datetime)
            
        Returns:
            StockPrice 對象或 None
        """
        # 處理日期類型轉換：date -> datetime
        from datetime import datetime
        if isinstance(price_date, date) and not isinstance(price_date, datetime):
            price_date = datetime.combine(price_date, datetime.min.time())
            
        return session.query(StockPrice).filter(
            and_(
                StockPrice.symbol == symbol,
                StockPrice.date == price_date
            )
        ).first()
    
    def get_latest_by_symbol(self, session: Session, symbol: str) -> Optional[StockPrice]:
        """
        獲取指定股票的最新價格
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            StockPrice 對象或 None
        """
        return session.query(StockPrice).filter(
            StockPrice.symbol == symbol
        ).order_by(desc(StockPrice.date)).first()
    
    def get_by_symbol_and_date_range(
        self,
        session: Session,
        symbol: str,
        start_date,
        end_date
    ) -> List[StockPrice]:
        """
        獲取指定日期範圍的價格數據
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            start_date: 開始日期 (date 或 datetime)
            end_date: 結束日期 (date 或 datetime)
            
        Returns:
            價格列表
        """
        # 處理日期類型轉換：date -> datetime
        from datetime import datetime
        if isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
            
        return session.query(StockPrice).filter(
            and_(
                StockPrice.symbol == symbol,
                StockPrice.date >= start_date,
                StockPrice.date <= end_date
            )
        ).order_by(asc(StockPrice.date)).all()
    
    def get_by_symbols(
        self, 
        session: Session, 
        symbols: List[str], 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[StockPrice]:
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
        query = session.query(StockPrice).filter(StockPrice.symbol.in_(symbols))
        
        if start_date:
            query = query.filter(StockPrice.date >= start_date)
        if end_date:
            query = query.filter(StockPrice.date <= end_date)
        
        return query.order_by(StockPrice.symbol, asc(StockPrice.date)).all()
    
    def get_by_symbol(self, session: Session, symbol: str) -> List[StockPrice]:
        """
        根據股票代碼獲取所有價格數據
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            價格列表
        """
        return session.query(StockPrice).filter(
            StockPrice.symbol == symbol
        ).order_by(asc(StockPrice.date)).all()
    
    def delete_by_symbol(self, session: Session, symbol: str) -> int:
        """
        刪除指定股票的所有價格數據
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            
        Returns:
            刪除的記錄數
        """
        try:
            deleted_count = session.query(StockPrice).filter(
                StockPrice.symbol == symbol
            ).delete()
            session.flush()
            return deleted_count
        except Exception:
            return 0
    
    def update(self, session: Session, price: StockPrice, **kwargs) -> StockPrice:
        """
        更新價格記錄
        
        Args:
            session: 數據庫會話
            price: 價格對象
            **kwargs: 更新的字段
            
        Returns:
            更新後的 StockPrice 對象
        """
        for key, value in kwargs.items():
            if hasattr(price, key):
                setattr(price, key, value)
        session.flush()
        return price
    
    def delete(self, session: Session, price: StockPrice) -> bool:
        """
        刪除價格記錄
        
        Args:
            session: 數據庫會話
            price: 價格對象
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            session.delete(price)
            session.flush()
            return True
        except Exception:
            return False
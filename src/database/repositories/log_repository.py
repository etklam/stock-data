"""
數據獲取日誌數據倉儲
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import DataFetchLog


class LogRepository:
    """數據獲取日誌數據倉儲"""
    
    def create(self, session: Session, **kwargs) -> DataFetchLog:
        """
        創建日誌記錄
        
        Args:
            session: 數據庫會話
            **kwargs: 日誌信息
            
        Returns:
            DataFetchLog 對象
        """
        log = DataFetchLog(**kwargs)
        session.add(log)
        session.flush()
        return log
    
    def get_recent(
        self, 
        session: Session, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[DataFetchLog]:
        """
        獲取最近的日誌記錄
        
        Args:
            session: 數據庫會話
            limit: 限制數量
            status: 狀態過濾（可選）
            
        Returns:
            日誌列表
        """
        query = session.query(DataFetchLog)
        
        if status:
            query = query.filter(DataFetchLog.status == status)
        
        return query.order_by(desc(DataFetchLog.created_at)).limit(limit).all()
    
    def get_by_symbol(
        self, 
        session: Session, 
        symbol: str, 
        limit: int = 50
    ) -> List[DataFetchLog]:
        """
        根據股票代碼獲取日誌記錄
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            limit: 限制數量
            
        Returns:
            日誌列表
        """
        return session.query(DataFetchLog).filter(
            DataFetchLog.symbol == symbol
        ).order_by(desc(DataFetchLog.created_at)).limit(limit).all()
    
    def get_by_fetch_type(
        self, 
        session: Session, 
        fetch_type: str, 
        limit: int = 50
    ) -> List[DataFetchLog]:
        """
        根據獲取類型獲取日誌記錄
        
        Args:
            session: 數據庫會話
            fetch_type: 獲取類型
            limit: 限制數量
            
        Returns:
            日誌列表
        """
        return session.query(DataFetchLog).filter(
            DataFetchLog.fetch_type == fetch_type
        ).order_by(desc(DataFetchLog.created_at)).limit(limit).all()
    
    def delete_old_logs(self, session: Session, days: int = 30) -> int:
        """
        刪除舊日誌記錄
        
        Args:
            session: 數據庫會話
            days: 保留天數
            
        Returns:
            int: 刪除的記錄數
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = session.query(DataFetchLog).filter(
            DataFetchLog.created_at < cutoff_date
        ).delete()
        
        session.flush()
        return deleted_count
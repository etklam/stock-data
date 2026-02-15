"""
數據獲取日誌服務
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from ..database.repositories.log_repository import LogRepository

logger = logging.getLogger(__name__)


class LogService:
    """數據獲取日誌服務"""
    
    def __init__(self) -> None:
        """初始化日誌服務"""
        self.log_repository = LogRepository()
    
    def create_log(
        self,
        session: Session,
        fetch_type: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: str = 'success',
        records_count: int = 0,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> bool:
        """
        創建數據獲取日誌
        
        Args:
            session: 數據庫會話
            fetch_type: 獲取類型
            symbol: 股票代碼（可選）
            start_date: 開始時間（可選）
            end_date: 結束時間（可選）
            status: 狀態
            records_count: 記錄數
            error_message: 錯誤信息（可選）
            execution_time: 執行時間（可選）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            self.log_repository.create(
                session,
                symbol=symbol,
                fetch_type=fetch_type,
                start_date=start_date,
                end_date=end_date,
                status=status,
                records_count=records_count,
                error_message=error_message,
                execution_time=execution_time
            )
            return True
        except Exception as e:
            logger.error(f"創建數據獲取日誌失敗: {e}")
            return False
    
    def get_recent_logs(
        self, 
        session: Session, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[object]:
        """
        獲取最近的日誌記錄
        
        Args:
            session: 數據庫會話
            limit: 限制數量
            status: 狀態過濾（可選）
            
        Returns:
            日誌列表
        """
        try:
            return self.log_repository.get_recent(session, limit, status)
        except Exception as e:
            logger.error(f"獲取最近日誌記錄失敗: {e}")
            return []
"""
數據庫操作服務 - 向後相容層
DEPRECATED: 此模組已拆分為 src/services/ 和 src/database/repositories/
建議直接使用新的服務模組和倉儲模組
"""

import warnings
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
import logging

# 發出棄用警告
warnings.warn(
    "src.database.services 模組已棄用，請使用 src.services 和 src.database.repositories 模組。"
    "此模組僅為向後相容性保留，未來版本可能移除。",
    DeprecationWarning,
    stacklevel=2
)

from .models import Stock, StockPrice, DataFetchLog, SystemConfig, StockCategory, StockCategoryMapping
from .connection import db_manager

logger = logging.getLogger(__name__)


# 向後相容的 StockService 類
class StockService:
    """股票信息服務 - 向後相容"""
    
    @staticmethod
    def create_or_update_stock(session: Session, symbol: str, **kwargs) -> Stock:
        """創建或更新股票信息"""
        from ..services.stock_service import StockService as NewStockService
        
        service = NewStockService()
        success = service.create_or_update_stock(session, symbol, **kwargs)
        
        if success:
            return session.query(Stock).filter(Stock.symbol == symbol).first()
        else:
            raise Exception("創建或更新股票失敗")
    
    @staticmethod
    def get_stock_by_symbol(session: Session, symbol: str) -> Optional[Stock]:
        """根據股票代碼獲取股票信息"""
        from ..services.stock_service import StockService as NewStockService
        
        service = NewStockService()
        return service.get_stock_by_symbol(session, symbol)
    
    @staticmethod
    def get_all_active_stocks(session: Session) -> List[Stock]:
        """獲取所有啟用的股票"""
        from ..services.stock_service import StockService as NewStockService
        
        service = NewStockService()
        return service.get_all_active_stocks(session)
    
    @staticmethod
    def get_stocks_by_exchange(session: Session, exchange: str) -> List[Stock]:
        """根據交易所獲取股票列表"""
        from ..services.stock_service import StockService as NewStockService
        
        service = NewStockService()
        return service.get_stocks_by_exchange(session, exchange)


# 向後相容的 StockPriceService 類
class StockPriceService:
    """股票價格服務 - 向後相容"""
    
    @staticmethod
    def save_stock_prices(session: Session, symbol: str, price_data: List[Dict[str, Any]]) -> int:
        """保存股票價格數據"""
        from ..services.price_service import PriceService
        
        service = PriceService()
        return service.save_stock_prices(session, symbol, price_data)
    
    @staticmethod
    def get_latest_price(session: Session, symbol: str) -> Optional[StockPrice]:
        """獲取股票最新價格"""
        from ..services.price_service import PriceService
        
        service = PriceService()
        return service.get_latest_price(session, symbol)
    
    @staticmethod
    def get_prices_by_date_range(
        session: Session, 
        symbol: str, 
        start_date: date, 
        end_date: date
    ) -> List[StockPrice]:
        """獲取指定日期範圍的價格數據"""
        from ..services.price_service import PriceService
        
        service = PriceService()
        return service.get_prices_by_date_range(session, symbol, start_date, end_date)
    
    @staticmethod
    def get_prices_by_symbols(
        session: Session, 
        symbols: List[str], 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[StockPrice]:
        """獲取多個股票的價格數據"""
        from ..services.price_service import PriceService
        
        service = PriceService()
        return service.get_prices_by_symbols(session, symbols, start_date, end_date)


# 向後相容的 DataFetchLogService 類
class DataFetchLogService:
    """數據獲取日誌服務 - 向後相容"""
    
    @staticmethod
    def create_log(
        session: Session,
        fetch_type: str,
        symbol: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: str = 'success',
        records_count: int = 0,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> DataFetchLog:
        """創建數據獲取日誌"""
        from ..services.log_service import LogService
        
        service = LogService()
        success = service.create_log(
            session, fetch_type, symbol, start_date, end_date,
            status, records_count, error_message, execution_time
        )
        
        if success:
            return session.query(DataFetchLog).filter(
                DataFetchLog.fetch_type == fetch_type,
                DataFetchLog.symbol == symbol,
                DataFetchLog.created_at >= datetime.utcnow()
            ).order_by(desc(DataFetchLog.created_at)).first()
        else:
            raise Exception("創建數據獲取日誌失敗")
    
    @staticmethod
    def get_recent_logs(
        session: Session, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[DataFetchLog]:
        """獲取最近的日誌記錄"""
        from ..services.log_service import LogService
        
        service = LogService()
        return service.get_recent_logs(session, limit, status)


# 向後相容的 SystemConfigService 類
class SystemConfigService:
    """系統配置服務 - 向後相容"""
    
    @staticmethod
    def get_config(session: Session, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        from ..services.config_service import ConfigService
        
        service = ConfigService()
        return service.get_config(session, key, default)
    
    @staticmethod
    def set_config(
        session: Session, 
        key: str, 
        value: Any, 
        description: Optional[str] = None
    ) -> SystemConfig:
        """設置配置值"""
        from ..services.config_service import ConfigService
        
        service = ConfigService()
        success = service.set_config(session, key, value, description)
        
        if success:
            return session.query(SystemConfig).filter(SystemConfig.key == key).first()
        else:
            raise Exception("設置配置值失敗")


# 向後相容的 StockCategoryService 類
class StockCategoryService:
    """股票分類服務 - 向後相容"""
    
    @staticmethod
    def create_category(
        session: Session,
        name: str,
        category_type: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: int = 0
    ) -> StockCategory:
        """創建股票分類"""
        from ..services.category_service import CategoryService
        
        service = CategoryService()
        success = service.create_category(
            session, name, category_type, description, parent_id, sort_order
        )
        
        if success:
            return session.query(StockCategory).filter(StockCategory.name == name).first()
        else:
            raise Exception("創建股票分類失敗")
    
    @staticmethod
    def get_categories_by_type(session: Session, category_type: str) -> List[StockCategory]:
        """根據類型獲取分類列表"""
        from ..services.category_service import CategoryService
        
        service = CategoryService()
        return service.get_categories_by_type(session, category_type)
    
    @staticmethod
    def get_all_categories(session: Session) -> List[StockCategory]:
        """獲取所有分類"""
        from ..services.category_service import CategoryService
        
        service = CategoryService()
        return service.get_all_categories(session)


# 向後相容的 StockCategoryMappingService 類
class StockCategoryMappingService:
    """股票分類映射服務 - 向後相容"""
    
    @staticmethod
    def create_mapping(
        session: Session,
        symbol: str,
        category_id: int,
        is_primary: bool = False
    ) -> StockCategoryMapping:
        """創建股票與分類的映射關係"""
        from ..database.repositories.category_repository import CategoryRepository
        
        repository = CategoryRepository()
        return repository.create_mapping(session, symbol, category_id, is_primary)
    
    @staticmethod
    def get_stocks_by_category(session: Session, category_id: int) -> List[str]:
        """獲取分類下的股票列表"""
        from ..database.repositories.category_repository import CategoryRepository
        
        repository = CategoryRepository()
        return repository.get_stocks_by_category(session, category_id)
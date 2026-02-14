"""
股票分類數據倉儲
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models import StockCategory, StockCategoryMapping


class CategoryRepository:
    """股票分類數據倉儲"""
    
    def create(self, session: Session, **kwargs) -> StockCategory:
        """
        創建分類記錄
        
        Args:
            session: 數據庫會話
            **kwargs: 分類信息
            
        Returns:
            StockCategory 對象
        """
        category = StockCategory(**kwargs)
        session.add(category)
        session.flush()
        return category
    
    def get_by_id(self, session: Session, category_id: int) -> Optional[StockCategory]:
        """
        根據ID獲取分類
        
        Args:
            session: 數據庫會話
            category_id: 分類ID
            
        Returns:
            StockCategory 對象或 None
        """
        return session.query(StockCategory).filter(StockCategory.id == category_id).first()
    
    def get_by_type(self, session: Session, category_type: str) -> List[StockCategory]:
        """
        根據類型獲取分類列表
        
        Args:
            session: 數據庫會話
            category_type: 分類類型
            
        Returns:
            分類列表
        """
        return session.query(StockCategory).filter(
            and_(
                StockCategory.type == category_type,
                StockCategory.is_active == True
            )
        ).order_by(StockCategory.sort_order).all()
    
    def get_all_active(self, session: Session) -> List[StockCategory]:
        """
        獲取所有啟用的分類
        
        Args:
            session: 數據庫會話
            
        Returns:
            分類列表
        """
        return session.query(StockCategory).filter(
            StockCategory.is_active == True
        ).order_by(StockCategory.type, StockCategory.sort_order).all()
    
    def get_children(self, session: Session, parent_id: int) -> List[StockCategory]:
        """
        獲取子分類
        
        Args:
            session: 數據庫會話
            parent_id: 父分類ID
            
        Returns:
            子分類列表
        """
        return session.query(StockCategory).filter(
            and_(
                StockCategory.parent_id == parent_id,
                StockCategory.is_active == True
            )
        ).order_by(StockCategory.sort_order).all()
    
    def update(self, session: Session, category: StockCategory, **kwargs) -> StockCategory:
        """
        更新分類記錄
        
        Args:
            session: 數據庫會話
            category: 分類對象
            **kwargs: 更新的字段
            
        Returns:
            更新後的 StockCategory 對象
        """
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
        session.flush()
        return category
    
    def delete(self, session: Session, category: StockCategory) -> bool:
        """
        刪除分類記錄（軟刪除）
        
        Args:
            session: 數據庫會話
            category: 分類對象
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            # 軟刪除：設置為不啟用
            category.is_active = False
            session.flush()
            return True
        except Exception:
            return False
    
    def create_mapping(
        self, 
        session: Session, 
        symbol: str, 
        category_id: int, 
        is_primary: bool = False
    ) -> StockCategoryMapping:
        """
        創建股票與分類的映射關係
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            category_id: 分類ID
            is_primary: 是否為主要分類
            
        Returns:
            StockCategoryMapping 對象
        """
        mapping = StockCategoryMapping(
            symbol=symbol,
            category_id=category_id,
            is_primary=is_primary
        )
        session.add(mapping)
        session.flush()
        return mapping
    
    def get_stocks_by_category(self, session: Session, category_id: int) -> List[str]:
        """
        獲取分類下的股票列表
        
        Args:
            session: 數據庫會話
            category_id: 分類ID
            
        Returns:
            股票代碼列表
        """
        mappings = session.query(StockCategoryMapping).filter(
            StockCategoryMapping.category_id == category_id
        ).all()
        
        return [mapping.symbol for mapping in mappings]
    
    def delete_mapping(self, session: Session, symbol: str, category_id: int) -> bool:
        """
        刪除股票與分類的映射關係
        
        Args:
            session: 數據庫會話
            symbol: 股票代碼
            category_id: 分類ID
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            mapping = session.query(StockCategoryMapping).filter(
                and_(
                    StockCategoryMapping.symbol == symbol,
                    StockCategoryMapping.category_id == category_id
                )
            ).first()
            
            if mapping:
                session.delete(mapping)
                session.flush()
            
            return True
        except Exception:
            return False
"""
股票分類服務
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from ..database.repositories.category_repository import CategoryRepository

logger = logging.getLogger(__name__)


class CategoryService:
    """股票分類服務"""
    
    def __init__(self) -> None:
        """初始化分類服務"""
        self.category_repository = CategoryRepository()
    
    def create_category(
        self,
        session: Session,
        name: str,
        category_type: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: int = 0
    ) -> bool:
        """
        創建股票分類
        
        Args:
            session: 數據庫會話
            name: 分類名稱
            category_type: 分類類型
            description: 分類描述（可選）
            parent_id: 父分類ID（可選）
            sort_order: 排序順序
            
        Returns:
            bool: 操作是否成功
        """
        try:
            self.category_repository.create(
                session,
                name=name,
                type=category_type,
                description=description,
                parent_id=parent_id,
                sort_order=sort_order
            )
            logger.info(f"創建股票分類: {name}")
            return True
        except Exception as e:
            logger.error(f"創建股票分類失敗: {e}")
            return False
    
    def get_category_by_id(self, session: Session, category_id: int) -> Optional[object]:
        """
        根據ID獲取分類
        
        Args:
            session: 數據庫會話
            category_id: 分類ID
            
        Returns:
            分類對象或 None
        """
        try:
            return self.category_repository.get_by_id(session, category_id)
        except Exception as e:
            logger.error(f"獲取分類失敗: {e}")
            return None
    
    def get_categories_by_type(self, session: Session, category_type: str) -> List[object]:
        """
        根據類型獲取分類列表
        
        Args:
            session: 數據庫會話
            category_type: 分類類型
            
        Returns:
            分類列表
        """
        try:
            return self.category_repository.get_by_type(session, category_type)
        except Exception as e:
            logger.error(f"根據類型獲取分類列表失敗: {e}")
            return []
    
    def get_all_categories(self, session: Session) -> List[object]:
        """
        獲取所有分類
        
        Args:
            session: 數據庫會話
            
        Returns:
            分類列表
        """
        try:
            return self.category_repository.get_all_active(session)
        except Exception as e:
            logger.error(f"獲取所有分類失敗: {e}")
            return []
    
    def update_category(
        self,
        session: Session,
        category_id: int,
        **kwargs
    ) -> bool:
        """
        更新分類信息
        
        Args:
            session: 數據庫會話
            category_id: 分類ID
            **kwargs: 更新的字段
            
        Returns:
            bool: 操作是否成功
        """
        try:
            category = self.category_repository.get_by_id(session, category_id)
            if not category:
                logger.error(f"分類不存在: {category_id}")
                return False
            
            self.category_repository.update(session, category, **kwargs)
            logger.info(f"更新分類信息: {category_id}")
            return True
        except Exception as e:
            logger.error(f"更新分類信息失敗: {e}")
            return False
    
    def delete_category(self, session: Session, category_id: int) -> bool:
        """
        刪除分類
        
        Args:
            session: 數據庫會話
            category_id: 分類ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            category = self.category_repository.get_by_id(session, category_id)
            if not category:
                logger.error(f"分類不存在: {category_id}")
                return False
            
            success = self.category_repository.delete(session, category)
            if success:
                logger.info(f"刪除分類: {category_id}")
            return success
        except Exception as e:
            logger.error(f"刪除分類失敗: {e}")
            return False
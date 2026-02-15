"""
系統配置服務
"""

from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from ..database.repositories.config_repository import ConfigRepository

logger = logging.getLogger(__name__)


class ConfigService:
    """系統配置服務"""
    
    def __init__(self) -> None:
        """初始化配置服務"""
        self.config_repository = ConfigRepository()
    
    def get_config(self, session: Session, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            session: 數據庫會話
            key: 配置鍵
            default: 默認值
            
        Returns:
            配置值
        """
        try:
            config = self.config_repository.get_by_key(session, key)
            return config.value if config else default
        except Exception as e:
            logger.error(f"獲取配置值失敗: {e}")
            return default
    
    def set_config(
        self, 
        session: Session, 
        key: str, 
        value: Any, 
        description: Optional[str] = None
    ) -> bool:
        """
        設置配置值
        
        Args:
            session: 數據庫會話
            key: 配置鍵
            value: 配置值
            description: 配置描述（可選）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            config = self.config_repository.get_by_key(session, key)
            
            if config:
                # 更新現有配置
                self.config_repository.update(
                    session, config, 
                    value=str(value), 
                    description=description
                )
            else:
                # 創建新配置
                self.config_repository.create(
                    session,
                    key=key,
                    value=str(value),
                    description=description
                )
            
            return True
        except Exception as e:
            logger.error(f"設置配置值失敗: {e}")
            return False
    
    def delete_config(self, session: Session, key: str) -> bool:
        """
        刪除配置
        
        Args:
            session: 數據庫會話
            key: 配置鍵
            
        Returns:
            bool: 操作是否成功
        """
        try:
            config = self.config_repository.get_by_key(session, key)
            if config:
                return self.config_repository.delete(session, config)
            return True  # 配置不存在，視為成功
        except Exception as e:
            logger.error(f"刪除配置失敗: {e}")
            return False
    
    def get_all_configs(self, session: Session) -> list:
        """
        獲取所有配置
        
        Args:
            session: 數據庫會話
            
        Returns:
            配置列表
        """
        try:
            return self.config_repository.get_all(session)
        except Exception as e:
            logger.error(f"獲取所有配置失敗: {e}")
            return []
"""
系統配置數據倉儲
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import SystemConfig


class ConfigRepository:
    """系統配置數據倉儲"""
    
    def create(self, session: Session, **kwargs) -> SystemConfig:
        """
        創建配置記錄
        
        Args:
            session: 數據庫會話
            **kwargs: 配置信息
            
        Returns:
            SystemConfig 對象
        """
        config = SystemConfig(**kwargs)
        session.add(config)
        session.flush()
        return config
    
    def get_by_key(self, session: Session, key: str) -> Optional[SystemConfig]:
        """
        根據鍵獲取配置
        
        Args:
            session: 數據庫會話
            key: 配置鍵
            
        Returns:
            SystemConfig 對象或 None
        """
        return session.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    def get_all(self, session: Session) -> List[SystemConfig]:
        """
        獲取所有配置
        
        Args:
            session: 數據庫會話
            
        Returns:
            配置列表
        """
        return session.query(SystemConfig).all()
    
    def update(self, session: Session, config: SystemConfig, **kwargs) -> SystemConfig:
        """
        更新配置記錄
        
        Args:
            session: 數據庫會話
            config: 配置對象
            **kwargs: 更新的字段
            
        Returns:
            更新後的 SystemConfig 對象
        """
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.utcnow()
        session.flush()
        return config
    
    def delete(self, session: Session, config: SystemConfig) -> bool:
        """
        刪除配置記錄
        
        Args:
            session: 數據庫會話
            config: 配置對象
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            session.delete(config)
            session.flush()
            return True
        except Exception:
            return False
    
    def delete_by_key(self, session: Session, key: str) -> bool:
        """
        根據鍵刪除配置
        
        Args:
            session: 數據庫會話
            key: 配置鍵
            
        Returns:
            bool: 是否刪除成功
        """
        try:
            config = self.get_by_key(session, key)
            if config:
                return self.delete(session, config)
            return True  # 配置不存在，視為成功
        except Exception:
            return False
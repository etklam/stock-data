"""
配置管理模塊
負責讀取和管理應用配置
支持從 config.yaml 讀取默認配置，並從環境變數覆蓋敏感配置
"""

import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """配置管理器"""

    # 環境變數映射配置
    ENV_MAPPING = {
        'database.host': 'DATABASE_HOST',
        'database.port': 'DATABASE_PORT',
        'database.name': 'DATABASE_NAME',
        'database.user': 'DATABASE_USER',
        'database.password': 'DATABASE_PASSWORD',
        'yahoo_finance.fetch_interval': 'YAHOO_FETCH_INTERVAL',
        'yahoo_finance.start_date': 'YAHOO_START_DATE',
        'scheduler.enabled': 'SCHEDULER_ENABLED',
        'scheduler.daily_fetch_time': 'DAILY_FETCH_TIME',
        'scheduler.max_retries': 'MAX_RETRIES',
        'scheduler.retry_interval': 'RETRY_INTERVAL',
        'logging.level': 'LOG_LEVEL',
        'logging.file': 'LOG_FILE',
        'logging.max_size': 'LOG_MAX_SIZE',
        'logging.backup_count': 'LOG_BACKUP_COUNT',
        'app.debug': 'APP_DEBUG',
        'app.name': 'APP_NAME',
        'app.version': 'APP_VERSION',
        'api.host': 'API_HOST',
        'api.port': 'API_PORT',
        'api.reload': 'API_RELOAD',
        'api.workers': 'API_WORKERS',
    }

    def __init__(self, config_path: str = "config.yaml", env_file: str = ".env", load_env: bool = True):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路徑
            env_file: 環境變數文件路徑
        """
        self.config_path = Path(config_path)
        self.env_file = Path(env_file)
        self.load_env = load_env
        self._config: Optional[Dict[str, Any]] = None
        if self.load_env:
            self._load_env()
        self._load_config()
    
    def _load_env(self) -> None:
        """加載環境變數文件"""
        if self.env_file.exists():
            load_dotenv(self.env_file)

    def _load_config(self) -> None:
        """加載配置文件並應用環境變數覆蓋"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)

            # 應用環境變數覆蓋
            self._apply_env_overrides()

        except Exception as e:
            raise RuntimeError(f"加載配置文件失敗: {e}") from e

    def _apply_env_overrides(self) -> None:
        """應用環境變數覆蓋配置值"""
        for config_key, env_var in self.ENV_MAPPING.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 設置嵌套配置值
                keys = config_key.split('.')
                value = self._convert_env_value(env_value)

                # 導航到正確的位置並設置值
                config = self._config
                for key in keys[:-1]:
                    if key not in config:
                        config[key] = {}
                    config = config[key]

                # 轉換環境變數值類型
                config[keys[-1]] = value

    def _convert_env_value(self, value: str) -> Any:
        """轉換環境變數值為適當的類型"""
        # 布爾值
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # 數字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value


        # 字符串
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key: 配置鍵，支持點號分隔的嵌套鍵（如 'database.host'）
            default: 默認值
            
        Returns:
            配置值
        """
        if self._config is None:
            return default
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_database_config(self) -> Dict[str, Any]:
        """獲取數據庫配置"""
        return self.get('database', {})
    
    def get_yahoo_finance_config(self) -> Dict[str, Any]:
        """獲取 Yahoo Finance 配置"""
        return self.get('yahoo_finance', {})
    
    def get_stock_categories_config(self) -> Dict[str, Any]:
        """獲取股票分類配置"""
        yahoo_config = self.get_yahoo_finance_config()
        return yahoo_config.get('categories', {})
    
    def get_enabled_category_types(self) -> List[str]:
        """獲取啟用的分類類型"""
        yahoo_config = self.get_yahoo_finance_config()
        return yahoo_config.get('enabled_category_types', ['industry'])
    
    def get_all_symbols(self) -> List[str]:
        """獲取所有配置的股票代碼"""
        categories_config = self.get_stock_categories_config()
        all_symbols = set()
        
        for category_type in categories_config.values():
            for category in category_type.values():
                if isinstance(category, dict) and 'symbols' in category:
                    all_symbols.update(category.get('symbols', []))
        
        return list(all_symbols)
    
    def get_symbols_by_category(self, category_type: str, category_key: str) -> List[str]:
        """根據分類獲取股票代碼"""
        categories_config = self.get_stock_categories_config()
        
        if category_type in categories_config and category_key in categories_config[category_type]:
            category = categories_config[category_type][category_key]
            if isinstance(category, dict) and 'symbols' in category:
                return category.get('symbols', [])
        
        return []
    
    def get_category_display_name(self, category_type: str, category_key: str) -> str:
        """獲取分類顯示名稱"""
        categories_config = self.get_stock_categories_config()
        
        if category_type in categories_config and category_key in categories_config[category_type]:
            category = categories_config[category_type][category_key]
            if isinstance(category, dict) and 'name' in category:
                return category.get('name', category_key)
        
        return category_key
    
    def get_scheduler_config(self) -> Dict[str, Any]:
        """獲取調度器配置"""
        return self.get('scheduler', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """獲取日誌配置"""
        return self.get('logging', {})
    
    def get_app_config(self) -> Dict[str, Any]:
        """獲取應用配置"""
        return self.get('app', {})
    
    def reload(self) -> None:
        """重新加載配置文件"""
        self._load_config()


# 全局配置實例
config = ConfigManager()
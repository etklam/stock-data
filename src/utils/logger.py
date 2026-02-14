"""
日誌配置模塊
"""

import logging
import logging.handlers
import os
from pathlib import Path

from ..config.config_manager import config


def setup_logging():
    """設置日誌配置"""
    # 獲取日誌配置
    log_config = config.get_logging_config()
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', 'logs/stocks_data.log')
    max_size = log_config.get('max_size', 10485760)  # 10MB
    backup_count = log_config.get('backup_count', 5)
    
    # 確保日誌目錄存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 創建根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除現有處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 創建格式器
    formatter = logging.Formatter(log_format)
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件處理器（輪轉）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 設置第三方庫日誌級別
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('yfinance').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    logging.info("日誌系統初始化完成")


def get_logger(name: str) -> logging.Logger:
    """
    獲取指定名稱的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        
    Returns:
        日誌記錄器
    """
    return logging.getLogger(name)
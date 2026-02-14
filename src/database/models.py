"""
數據庫模型定義
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Stock(Base):
    """股票基本信息表"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, comment='股票代碼')
    name = Column(String(100), nullable=True, comment='股票名稱')
    exchange = Column(String(20), nullable=True, comment='交易所')
    sector = Column(String(50), nullable=True, comment='行業')
    industry = Column(String(100), nullable=True, comment='產業')
    market_cap = Column(Float, nullable=True, comment='市值')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新時間')
    is_active = Column(Boolean, default=True, comment='是否啟用')
    
    # 創建索引
    __table_args__ = (
        Index('idx_stock_symbol', 'symbol'),
        Index('idx_stock_exchange', 'exchange'),
        Index('idx_stock_active', 'is_active'),
    )


class StockPrice(Base):
    """股票價格數據表"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment='股票代碼')
    date = Column(DateTime, nullable=False, comment='日期')
    open_price = Column(Float, nullable=False, comment='開盤價')
    high_price = Column(Float, nullable=False, comment='最高價')
    low_price = Column(Float, nullable=False, comment='最低價')
    close_price = Column(Float, nullable=False, comment='收盤價')
    adj_close = Column(Float, nullable=True, comment='調整後收盤價')
    volume = Column(Integer, nullable=False, comment='成交量')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    
    # 創建複合索引
    __table_args__ = (
        Index('idx_price_symbol_date', 'symbol', 'date'),
        Index('idx_price_date', 'date'),
    )


class DataFetchLog(Base):
    """數據獲取日誌表"""
    __tablename__ = 'data_fetch_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=True, comment='股票代碼')
    fetch_type = Column(String(20), nullable=False, comment='獲取類型（historical/daily）')
    start_date = Column(DateTime, nullable=True, comment='開始日期')
    end_date = Column(DateTime, nullable=True, comment='結束日期')
    status = Column(String(20), nullable=False, comment='狀態（success/failed/partial）')
    records_count = Column(Integer, default=0, comment='獲取記錄數')
    error_message = Column(Text, nullable=True, comment='錯誤信息')
    execution_time = Column(Float, nullable=True, comment='執行時間（秒）')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    
    # 創建索引
    __table_args__ = (
        Index('idx_log_symbol', 'symbol'),
        Index('idx_log_status', 'status'),
        Index('idx_log_created_at', 'created_at'),
    )


class StockCategory(Base):
    """股票分類表"""
    __tablename__ = 'stock_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment='分類名稱')
    type = Column(String(20), nullable=False, comment='分類類型（industry/region/market_cap/custom）')
    description = Column(String(200), nullable=True, comment='分類描述')
    parent_id = Column(Integer, nullable=True, comment='父分類ID（支持層級分類）')
    sort_order = Column(Integer, default=0, comment='排序順序')
    is_active = Column(Boolean, default=True, comment='是否啟用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新時間')
    
    # 創建索引
    __table_args__ = (
        Index('idx_category_type', 'type'),
        Index('idx_category_parent', 'parent_id'),
        Index('idx_category_active', 'is_active'),
    )


class StockCategoryMapping(Base):
    """股票分類映射表"""
    __tablename__ = 'stock_category_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, comment='股票代碼')
    category_id = Column(Integer, nullable=False, comment='分類ID')
    is_primary = Column(Boolean, default=False, comment='是否為主要分類')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    
    # 創建複合索引和唯一約束
    __table_args__ = (
        Index('idx_mapping_symbol', 'symbol'),
        Index('idx_mapping_category', 'category_id'),
        Index('idx_mapping_primary', 'is_primary'),
        # 確保同一股票在同一分類中只有一條記錄
        Index('uq_symbol_category', 'symbol', 'category_id', unique=True),
    )


class SystemConfig(Base):
    """系統配置表"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment='配置鍵')
    value = Column(Text, nullable=True, comment='配置值')
    description = Column(String(200), nullable=True, comment='配置描述')
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新時間')
    
    # 創建索引
    __table_args__ = (
        Index('idx_config_key', 'key'),
    )
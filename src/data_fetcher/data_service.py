"""
數據獲取服務
整合 Yahoo Finance 數據獲取和數據庫存儲
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import time

from .yahoo_client import YahooFinanceClient
from ..database.connection import db_manager
from ..database.services import StockService, StockPriceService, DataFetchLogService, StockCategoryService, StockCategoryMappingService
from ..config.config_manager import config

logger = logging.getLogger(__name__)


class DataFetchService:
    """數據獲取服務"""
    
    def __init__(self):
        """初始化服務"""
        self.yahoo_client = YahooFinanceClient()
        self.symbols = config.get_all_symbols()
        self.start_date = config.get('yahoo_finance.start_date', '2020-01-01')
    
    def fetch_and_store_stock_info(self, symbol: str) -> bool:
        """
        獲取並存儲股票基本信息
        
        Args:
            symbol: 股票代碼
            
        Returns:
            是否成功
        """
        try:
            with db_manager.session_scope() as session:
                # 獲取股票信息
                stock_info = self.yahoo_client.get_stock_info(symbol)
                if not stock_info:
                    logger.error(f"無法獲取股票信息: {symbol}")
                    return False
                
                # 創建服務實例
                stock_service = StockService()
                
                # 從 stock_info 中移除 symbol，避免重複傳遞
                stock_data = {k: v for k, v in stock_info.items() if k != 'symbol'}
                
                # 存儲到數據庫
                stock_service.create_or_update_stock(session, symbol, **stock_data)
                
                logger.info(f"股票信息存儲成功: {symbol}")
                return True
                
        except Exception as e:
            logger.error(f"獲取股票信息失敗 {symbol}: {e}")
            return False
    
    def fetch_and_store_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Tuple[bool, int]:
        """
        獲取並存儲歷史數據
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            (是否成功, 記錄數)
        """
        start_time = time.time()
        
        try:
            # 使用默認日期如果未提供
            if not start_date:
                start_date = self.start_date
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 獲取歷史數據
            hist_data = self.yahoo_client.get_historical_data(symbol, start_date, end_date)
            if hist_data is None or hist_data.empty:
                logger.warning(f"未獲取到歷史數據: {symbol}")
                return False, 0
            
            # 轉換數據格式
            price_data = []
            for _, row in hist_data.iterrows():
                price_record = {
                    'date': pd.to_datetime(row['date']).to_pydatetime(),
                    'open_price': float(row['open']),
                    'high_price': float(row['high']),
                    'low_price': float(row['low']),
                    'close_price': float(row['close']),
                    'adj_close': float(row.get('adj_close', row['close'])),
                    'volume': int(row['volume']),
                }
                price_data.append(price_record)
            
            # 存儲到數據庫
            with db_manager.session_scope() as session:
                # 創建服務實例
                price_service = StockPriceService()
                log_service = DataFetchLogService()
                
                saved_count = price_service.save_stock_prices(session, symbol, price_data)
                
                # 記錄日誌
                execution_time = time.time() - start_time
                log_service.create_log(
                    session,
                    fetch_type='historical',
                    symbol=symbol,
                    start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                    end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                    status='success',
                    records_count=saved_count,
                    execution_time=execution_time
                )
            
            logger.info(f"歷史數據存儲成功: {symbol}, 記錄數: {saved_count}")
            return True, saved_count
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            # 記錄錯誤日誌
            try:
                with db_manager.session_scope() as session:
                    log_service = DataFetchLogService()
                    log_service.create_log(
                        session,
                        fetch_type='historical',
                        symbol=symbol,
                        start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
                        end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None,
                        status='failed',
                        error_message=error_msg,
                        execution_time=execution_time
                    )
            except Exception as log_error:
                logger.error(f"記錄錯誤日誌失敗: {log_error}")
            
            logger.error(f"獲取歷史數據失敗 {symbol}: {e}")
            return False, 0
    
    def fetch_and_store_daily_data(self, symbol: str) -> bool:
        """
        獲取並存儲每日數據（最新數據）
        
        Args:
            symbol: 股票代碼
            
        Returns:
            是否成功
        """
        try:
            # 獲取最新價格
            price_info = self.yahoo_client.get_latest_price(symbol)
            if not price_info:
                logger.error(f"無法獲取最新價格: {symbol}")
                return False
            
            # 存儲到數據庫
            with db_manager.session_scope() as session:
                # 創建服務實例
                price_service = StockPriceService()
                log_service = DataFetchLogService()
                
                saved_count = price_service.save_stock_prices(session, symbol, [price_info])
                
                # 記錄日誌
                log_service.create_log(
                    session,
                    fetch_type='daily',
                    symbol=symbol,
                    status='success',
                    records_count=saved_count
                )
            
            logger.info(f"每日數據存儲成功: {symbol}")
            return True
            
        except Exception as e:
            # 記錄錯誤日誌
            try:
                with db_manager.session_scope() as session:
                    log_service = DataFetchLogService()
                    log_service.create_log(
                        session,
                        fetch_type='daily',
                        symbol=symbol,
                        status='failed',
                        error_message=str(e)
                    )
            except Exception as log_error:
                logger.error(f"記錄錯誤日誌失敗: {log_error}")
            
            logger.error(f"獲取每日數據失敗 {symbol}: {e}")
            return False
    
    def fetch_all_stocks_historical(self) -> Dict[str, Tuple[bool, int]]:
        """
        獲取所有股票的歷史數據
        
        Returns:
            股票代碼到 (是否成功, 記錄數) 的映射
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                success, count = self.fetch_and_store_historical_data(symbol)
                results[symbol] = (success, count)
                
                # 添加延遲以避免觸發 API 限制
                time.sleep(self.yahoo_client.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"獲取歷史數據異常 {symbol}: {e}")
                results[symbol] = (False, 0)
        
        return results
    
    def fetch_all_stocks_daily(self) -> Dict[str, bool]:
        """
        獲取所有股票的每日數據
        
        Returns:
            股票代碼到是否成功的映射
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                success = self.fetch_and_store_daily_data(symbol)
                results[symbol] = success
                
                # 添加延遲以避免觸發 API 限制
                time.sleep(self.yahoo_client.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"獲取每日數據異常 {symbol}: {e}")
                results[symbol] = False
        
        return results
    
    def update_stock_info_for_all(self) -> Dict[str, bool]:
        """
        更新所有股票的基本信息
        
        Returns:
            股票代碼到是否成功的映射
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                success = self.fetch_and_store_stock_info(symbol)
                results[symbol] = success
                
                # 添加延遲以避免觸發 API 限制
                time.sleep(self.yahoo_client.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"更新股票信息異常 {symbol}: {e}")
                results[symbol] = False
        
        return results
    
    def get_missing_data_dates(self, symbol: str) -> List[date]:
        """
        獲取缺失數據的日期列表
        
        Args:
            symbol: 股票代碼
            
        Returns:
            缺失數據的日期列表
        """
        try:
            with db_manager.session_scope() as session:
                # 獲取數據庫中最新的日期
                latest_price = StockPriceService.get_latest_price(session, symbol)
                
                if not latest_price:
                    # 如果沒有數據，返回從配置的開始日期到今天
                    start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
                else:
                    # 從最新日期的下一天開始
                    start_date = latest_price.date.date() + timedelta(days=1)
                
                end_date = datetime.now().date()
                
                # 生成日期範圍
                missing_dates = []
                current_date = start_date
                
                while current_date <= end_date:
                    # 檢查是否為交易日（排除週末）
                    if current_date.weekday() < 5:  # 0-4 表示週一到週五
                        missing_dates.append(current_date)
                    current_date += timedelta(days=1)
                
                return missing_dates
                
        except Exception as e:
            logger.error(f"獲取缺失數據日期失敗 {symbol}: {e}")
            return []
    
    def initialize_categories_from_config(self) -> bool:
        """
        從配置文件初始化股票分類
        
        Returns:
            是否成功
        """
        try:
            categories_config = config.get_stock_categories_config()
            enabled_types = config.get_enabled_category_types()
            
            with db_manager.session_scope() as session:
                # 創建分類
                for category_type, categories in categories_config.items():
                    if category_type not in enabled_types:
                        continue
                    
                    for category_key, category_info in categories.items():
                        if not isinstance(category_info, dict):
                            continue
                        
                        # 創建分類
                        category = StockCategoryService.create_category(
                            session=session,
                            name=category_info.get('name', category_key),
                            category_type=category_type,
                            description=f"{category_type} 分類: {category_info.get('name', category_key)}"
                        )
                        
                        # 添加股票到分類
                        symbols = category_info.get('symbols', [])
                        for symbol in symbols:
                            StockCategoryMappingService.add_stock_to_category(
                                session=session,
                                symbol=symbol,
                                category_id=category.id,
                                is_primary=(category_type == enabled_types[0])  # 第一個啟用的類型作為主要分類
                            )
            
            logger.info("股票分類初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"股票分類初始化失敗: {e}")
            return False
    
    def fetch_and_store_by_category(self, category_type: str, category_key: str) -> Tuple[bool, int]:
        """
        根據分類獲取並存儲歷史數據
        
        Args:
            category_type: 分類類型
            category_key: 分類鍵
            
        Returns:
            (是否成功, 總記錄數)
        """
        try:
            symbols = config.get_symbols_by_category(category_type, category_key)
            if not symbols:
                logger.warning(f"分類 {category_type}.{category_key} 中沒有股票")
                return False, 0
            
            total_records = 0
            success_count = 0
            
            for symbol in symbols:
                try:
                    success, count = self.fetch_and_store_historical_data(symbol)
                    if success:
                        success_count += 1
                        total_records += count
                    
                    # 添加延遲以避免觸發 API 限制
                    time.sleep(self.yahoo_client.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"獲取分類數據失敗 {symbol}: {e}")
                    continue
            
            logger.info(f"分類 {category_type}.{category_key} 數據獲取完成: {success_count}/{len(symbols)} 成功, 總記錄數: {total_records}")
            return success_count > 0, total_records
            
        except Exception as e:
            logger.error(f"根據分類獲取數據失敗 {category_type}.{category_key}: {e}")
            return False, 0
    
    def fetch_and_store_by_category_type(self, category_type: str) -> Dict[str, Tuple[bool, int]]:
        """
        根據分類類型獲取所有分類的數據
        
        Args:
            category_type: 分類類型
            
        Returns:
            分類鍵到 (是否成功, 記錄數) 的映射
        """
        results = {}
        categories_config = config.get_stock_categories_config()
        
        if category_type not in categories_config:
            logger.error(f"不存在的分類類型: {category_type}")
            return results
        
        for category_key in categories_config[category_type].keys():
            success, count = self.fetch_and_store_by_category(category_type, category_key)
            results[category_key] = (success, count)
        
        return results
    
    def get_stocks_by_category_from_db(self, category_type: str, category_key: str) -> List[str]:
        """
        從數據庫獲取分類下的股票
        
        Args:
            category_type: 分類類型
            category_key: 分類鍵
            
        Returns:
            股票代碼列表
        """
        try:
            with db_manager.session_scope() as session:
                # 獲取分類
                category = session.query(StockCategory).filter(
                    and_(
                        StockCategory.type == category_type,
                        StockCategory.name == config.get_category_display_name(category_type, category_key)
                    )
                ).first()
                
                if not category:
                    logger.warning(f"找不到分類: {category_type}.{category_key}")
                    return []
                
                # 獲取分類下的股票
                return StockCategoryMappingService.get_stocks_by_category(session, category.id)
                
        except Exception as e:
            logger.error(f"獲取分類股票失敗 {category_type}.{category_key}: {e}")
            return []
    
    def get_all_categories_with_stocks(self) -> Dict[str, Dict[str, List[str]]]:
        """
        獲取所有分類及其股票
        
        Returns:
            分類類型到分類鍵到股票列表的映射
        """
        result = {}
        enabled_types = config.get_enabled_category_types()
        
        for category_type in enabled_types:
            result[category_type] = {}
            
            with db_manager.session_scope() as session:
                categories = StockCategoryService.get_categories_by_type(session, category_type)
                
                for category in categories:
                    stocks = StockCategoryMappingService.get_stocks_by_category(session, category.id)
                    result[category_type][category.name] = stocks
        
        return result
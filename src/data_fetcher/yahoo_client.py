"""
Yahoo Finance 數據獲取客戶端
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import time
import logging

from ..config.config_manager import config

logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """Yahoo Finance API 客戶端"""
    
    def __init__(self):
        """初始化客戶端"""
        self.rate_limit_delay = 1  # 請求間隔（秒）
        self.max_retries = 3
        self.timeout = 30
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        獲取股票基本信息
        
        Args:
            symbol: 股票代碼
            
        Returns:
            股票信息字典
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 提取有用的信息（只包含 Stock 模型中存在的字段）
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', '')),
                'exchange': info.get('exchange', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
            }
            
            logger.info(f"獲取股票信息成功: {symbol}")
            return stock_info
            
        except Exception as e:
            logger.error(f"獲取股票信息失敗 {symbol}: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        獲取歷史價格數據
        
        Args:
            symbol: 股票代碼
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            period: 周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            歷史數據 DataFrame
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # 構建參數
            kwargs = {}
            if start_date and end_date:
                kwargs['start'] = start_date
                kwargs['end'] = end_date
            elif period:
                kwargs['period'] = period
            else:
                # 默認獲取過去一年的數據
                kwargs['period'] = '1y'
            
            # 獲取歷史數據
            hist = ticker.history(**kwargs, timeout=self.timeout)
            
            if hist.empty:
                logger.warning(f"未獲取到歷史數據: {symbol}")
                return None
            
            # 重置索引，將日期變為列
            hist.reset_index(inplace=True)
            
            # 標準化列名
            hist.columns = [col.lower().replace(' ', '_') for col in hist.columns]
            
            logger.info(f"獲取歷史數據成功: {symbol}, 記錄數: {len(hist)}")
            return hist
            
        except Exception as e:
            logger.error(f"獲取歷史數據失敗 {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[Dict]:
        """
        獲取最新價格
        
        Args:
            symbol: 股票代碼
            
        Returns:
            最新價格信息
        """
        try:
            # 獲取最近一天的數據
            hist = self.get_historical_data(symbol, period='5d')
            if hist is None or hist.empty:
                return None
            
            # 獲取最後一條記錄
            latest = hist.iloc[-1]
            
            price_info = {
                'symbol': symbol,
                'date': latest['date'] if 'date' in latest else datetime.now(),
                'open_price': float(latest['open']),
                'high_price': float(latest['high']),
                'low_price': float(latest['low']),
                'close_price': float(latest['close']),
                'adj_close': float(latest.get('adj_close', latest['close'])),
                'volume': int(latest['volume']),
            }
            
            logger.info(f"獲取最新價格成功: {symbol}")
            return price_info
            
        except Exception as e:
            logger.error(f"獲取最新價格失敗 {symbol}: {e}")
            return None
    
    def get_multiple_stocks_data(
        self, 
        symbols: List[str], 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        批量獲取多個股票的數據
        
        Args:
            symbols: 股票代碼列表
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            股票代碼到數據的映射
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_historical_data(symbol, start_date, end_date)
                if data is not None:
                    results[symbol] = data
                
                # 添加延遲以避免觸發速率限制
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"批量獲取數據失敗 {symbol}: {e}")
                continue
        
        logger.info(f"批量獲取完成，成功: {len(results)}/{len(symbols)}")
        return results
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        驗證股票代碼是否有效
        
        Args:
            symbol: 股票代碼
            
        Returns:
            是否有效
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 檢查關鍵字段
            if info.get('regularMarketPrice') is None and info.get('currentPrice') is None:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"驗證股票代碼失敗 {symbol}: {e}")
            return False
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索股票
        
        Args:
            query: 搜索關鍵詞
            limit: 返回結果數量限制
            
        Returns:
            搜索結果列表
        """
        try:
            # yfinance 沒有直接的搜索功能，這裡提供一個簡單的實現
            # 實際應用中可能需要使用其他 API 或數據源
            logger.warning("yfinance 不支持搜索功能，返回空列表")
            return []
            
        except Exception as e:
            logger.error(f"搜索股票失敗: {e}")
            return []
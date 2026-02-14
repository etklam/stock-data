"""
Yahoo Finance 客戶端測試
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from src.data_fetcher.yahoo_client import YahooFinanceClient


class TestYahooFinanceClient:
    """Yahoo Finance 客戶端測試"""

    @pytest.fixture
    def client(self):
        """創建客戶端實例"""
        return YahooFinanceClient()

    def test_init_client(self):
        """測試初始化客戶端"""
        client = YahooFinanceClient()
        assert client is not None

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_stock_info_success(self, mock_ticker, client):
        """測試成功獲取股票信息"""
        # 模擬 yfinance 返回數據
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance

        mock_info = {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'exchange': 'NMS',
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        mock_ticker_instance.info = mock_info

        # 調用
        info = client.get_stock_info('AAPL')

        # 驗證
        assert info['symbol'] == 'AAPL'
        assert info['name'] == 'Apple Inc.'
        assert info['exchange'] == 'NMS'
        assert info['sector'] == 'Technology'

        mock_ticker.assert_called_once_with('AAPL')

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_stock_info_error(self, mock_ticker, client):
        """測試獲取股票信息失敗"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = None
        mock_ticker.return_value = mock_ticker_instance

        info = client.get_stock_info('INVALID_SYMBOL')

        assert info is None

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_historical_data_success(self, mock_ticker, client):
        """測試成功獲取歷史數據"""
        # 模擬歷史數據
        import pandas as pd

        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance

        # 創建模擬數據框
        mock_data = pd.DataFrame({
            'Open': [185.5, 187.5],
            'High': [188.0, 189.0],
            'Low': [184.5, 186.0],
            'Close': [187.0, 188.5],
            'Volume': [50000000, 45000000],
            'Adj Close': [187.0, 188.5]
        }, index=pd.date_range('2024-01-01', periods=2))

        mock_ticker_instance.history.return_value = mock_data

        # 調用
        data = client.get_historical_data('AAPL', date(2024, 1, 1), date(2024, 1, 2))

        # 驗證
        assert len(data) == 2
        assert data[0]['open_price'] == 185.5
        assert data[0]['close_price'] == 187.0
        assert data[0]['volume'] == 50000000

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_historical_data_empty(self, mock_ticker, client):
        """測試獲取歷史數據返回空結果"""
        import pandas as pd

        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance

        # 空數據框
        mock_data = pd.DataFrame()
        mock_ticker_instance.history.return_value = mock_data

        data = client.get_historical_data('AAPL', date(2024, 1, 1), date(2024, 1, 2))

        assert data == []

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_current_price_success(self, mock_ticker, client):
        """測試成功獲取當前價格"""
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance

        # 模擬最新價格
        mock_info = {
            'currentPrice': 188.5,
            'regularMarketPrice': 188.5
        }
        mock_ticker_instance.info = mock_info

        price = client.get_current_price('AAPL')

        assert price == 188.5

    @patch('src.data_fetcher.yahoo_client.yf.Ticker')
    def test_get_current_price_not_available(self, mock_ticker, client):
        """測試當前價格不可用"""
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.info = {}

        price = client.get_current_price('AAPL')

        assert price is None

    def test_validate_symbol_valid(self, client):
        """測試驗證有效的股票代碼"""
        assert client.validate_symbol('AAPL') is True
        assert client.validate_symbol('MSFT') is True
        assert client.validate_symbol('2330.TW') is True

    def test_validate_symbol_invalid(self, client):
        """測試驗證無效的股票代碼"""
        assert client.validate_symbol('') is False
        assert client.validate_symbol('AA') is False
        assert client.validate_symbol('123') is False

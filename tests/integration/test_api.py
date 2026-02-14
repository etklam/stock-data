"""
API 集成測試
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from api_server import app


@pytest.fixture
def client():
    """創建測試客戶端"""
    return TestClient(app)


class TestHealthEndpoints:
    """健康檢查端點測試"""

    def test_root_endpoint(self, client):
        """測試根端點"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data

    def test_health_check(self, client):
        """測試健康檢查端點"""
        with patch('src.database.connection.db_manager.test_connection', return_value=True):
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'healthy'
            assert data['database'] == 'connected'


class TestStockEndpoints:
    """股票端點測試"""

    def test_get_all_stocks_empty(self, client):
        """測試獲取所有股票（空列表）"""
        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.all.return_value = []

            response = client.get("/api/v1/stocks")

            assert response.status_code == 200
            data = response.json()
            assert data == []

    def test_get_all_stocks(self, client, sample_stocks_data):
        """測試獲取所有股票"""
        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            # 模擬股票數據
            mock_stocks = []
            for stock_data in sample_stocks_data:
                stock = Mock()
                stock.symbol = stock_data['symbol']
                stock.name = stock_data['name']
                stock.exchange = stock_data['exchange']
                stock.sector = stock_data['sector']
                stock.to_dict.return_value = stock_data
                mock_stocks.append(stock)

            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.all.return_value = mock_stocks

            response = client.get("/api/v1/stocks")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert data[0]['symbol'] == 'AAPL'

    def test_get_stock_by_symbol(self, client):
        """測試獲取特定股票"""
        mock_stock = Mock()
        mock_stock.symbol = 'AAPL'
        mock_stock.name = 'Apple Inc.'
        mock_stock.to_dict.return_value = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.'
        }

        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_stock

            response = client.get("/api/v1/stocks/AAPL")

            assert response.status_code == 200
            data = response.json()
            assert data['symbol'] == 'AAPL'
            assert data['name'] == 'Apple Inc.'

    def test_get_stock_not_found(self, client):
        """測試獲取不存在的股票"""
        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = None

            response = client.get("/api/v1/stocks/NONEXIST")

            assert response.status_code == 404


class TestPriceEndpoints:
    """價格端點測試"""

    def test_get_stock_prices(self, client, sample_price_data):
        """測試獲取股票價格"""
        mock_prices = []
        for price_data in sample_price_data:
            mock_price = Mock()
            mock_price.date = price_data['date']
            mock_price.open_price = price_data['open_price']
            mock_price.high_price = price_data['high_price']
            mock_price.low_price = price_data['low_price']
            mock_price.close_price = price_data['close_price']
            mock_price.volume = price_data['volume']
            mock_price.to_dict.return_value = price_data
            mock_prices.append(mock_price)

        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_prices

            response = client.get("/api/v1/stocks/AAPL/prices?limit=10")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]['symbol'] == 'AAPL'

    def test_get_latest_price(self, client):
        """測試獲取最新價格"""
        mock_price = Mock()
        mock_price.date = '2024-01-02'
        mock_price.close_price = 188.5
        mock_price.to_dict.return_value = {
            'date': '2024-01-02',
            'close_price': 188.5
        }

        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_price

            response = client.get("/api/v1/stocks/AAPL/prices/latest")

            assert response.status_code == 200
            data = response.json()
            assert data['close_price'] == 188.5

    def test_get_batch_prices(self, client):
        """測試批量獲取價格"""
        with patch('src.database.connection.db_manager.session_scope') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.all.return_value = []

            response = client.get("/api/v1/prices/batch?symbols=AAPL&symbols=MSFT")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)


class TestFetchEndpoints:
    """數據獲取端點測試"""

    def test_fetch_historical(self, client):
        """測試獲取歷史數據端點"""
        with patch('src.data_fetcher.data_service.DataFetchService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.fetch_and_store_historical_data.return_value = (True, 100)

            response = client.post(
                "/api/v1/fetch/historical",
                json={
                    "symbol": "AAPL",
                    "start_date": "2024-01-01"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'success'

    def test_fetch_daily(self, client):
        """測試獲取每日數據端點"""
        with patch('src.data_fetcher.data_service.DataFetchService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.fetch_and_store_daily_data.return_value = True

            response = client.post(
                "/api/v1/fetch/daily",
                json={"symbol": "AAPL"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'success'

    def test_fetch_batch_historical(self, client):
        """測試批量獲取歷史數據"""
        with patch('src.data_fetcher.data_service.DataFetchService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.fetch_batch_historical.return_value = {'AAPL': (True, 100)}

            response = client.post(
                "/api/v1/fetch/batch-historical",
                json={"symbols": ["AAPL", "MSFT"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert 'results' in data

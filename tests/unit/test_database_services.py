"""
數據庫服務測試
"""

import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Stock, StockPrice
from src.database.services import StockService, StockPriceService
from src.database.connection import DatabaseManager


@pytest.fixture
def in_memory_db():
    """創建內存數據庫用於測試"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestStockService:
    """股票服務測試"""

    def test_create_stock(self, in_memory_db):
        """測試創建新股票"""
        stock = StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NMS',
            sector='Technology',
            industry='Consumer Electronics'
        )

        assert stock.symbol == 'AAPL'
        assert stock.name == 'Apple Inc.'
        assert stock.exchange == 'NMS'
        assert stock.sector == 'Technology'
        assert stock.industry == 'Consumer Electronics'
        assert stock.is_active is True

    def test_update_stock(self, in_memory_db):
        """測試更新現有股票"""
        # 先創建
        StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NMS'
        )
        in_memory_db.commit()

        # 更新
        stock = StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc. Updated',
            exchange='NMS',
            sector='Technology'
        )

        assert stock.name == 'Apple Inc. Updated'
        assert stock.sector == 'Technology'

    def test_get_stock_by_symbol(self, in_memory_db):
        """測試根據股票代碼查詢"""
        # 創建測試數據
        StockService.create_or_update_stock(
            in_memory_db,
            symbol='MSFT',
            name='Microsoft Corporation'
        )
        in_memory_db.commit()

        # 查詢
        stock = StockService.get_stock_by_symbol(in_memory_db, 'MSFT')

        assert stock is not None
        assert stock.symbol == 'MSFT'
        assert stock.name == 'Microsoft Corporation'

    def test_get_stock_by_symbol_not_found(self, in_memory_db):
        """測試查詢不存在的股票"""
        stock = StockService.get_stock_by_symbol(in_memory_db, 'NONEXIST')
        assert stock is None

    def test_get_all_active_stocks(self, in_memory_db):
        """測試獲取所有啟用的股票"""
        # 創建測試數據
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')
        StockService.create_or_update_stock(in_memory_db, symbol='MSFT', name='Microsoft')
        StockService.create_or_update_stock(in_memory_db, symbol='GOOGL', name='Google', is_active=False)
        in_memory_db.commit()

        # 獲取啟用的股票
        stocks = StockService.get_all_active_stocks(in_memory_db)

        assert len(stocks) == 2
        symbols = [s.symbol for s in stocks]
        assert 'AAPL' in symbols
        assert 'MSFT' in symbols
        assert 'GOOGL' not in symbols


class TestStockPriceService:
    """股票價格服務測試"""

    def test_save_stock_prices(self, in_memory_db, sample_price_data):
        """測試保存股票價格"""
        # 先創建股票
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')

        # 保存價格
        count = StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)

        assert count == 2

        # 驗證數據
        prices = in_memory_db.query(StockPrice).filter_by(symbol='AAPL').all()
        assert len(prices) == 2
        assert prices[0].close_price == 187.0
        assert prices[1].close_price == 188.5

    def test_save_stock_prices_duplicate(self, in_memory_db, sample_price_data):
        """測試保存重複價格數據（應更新）"""
        # 創建股票
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')

        # 第一次保存
        StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)
        in_memory_db.commit()

        # 修改並第二次保存（更新）
        sample_price_data[0]['close_price'] = 190.0
        count = StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)

        # 應該更新而不是創建新記錄
        prices = in_memory_db.query(StockPrice).filter_by(symbol='AAPL').all()
        assert len(prices) == 2
        assert prices[0].close_price == 190.0  # 已更新

    def test_get_prices_by_symbol(self, in_memory_db, sample_price_data):
        """測試根據股票代碼獲取價格"""
        # 準備數據
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')
        StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)
        in_memory_db.commit()

        # 查詢價格
        prices = StockPriceService.get_prices_by_symbol(in_memory_db, 'AAPL')

        assert len(prices) == 2
        assert prices[0].symbol == 'AAPL'
        assert prices[0].date == date(2024, 1, 1)

    def test_get_latest_price(self, in_memory_db, sample_price_data):
        """測試獲取最新價格"""
        # 準備數據
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')
        StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)
        in_memory_db.commit()

        # 獲取最新價格
        latest_price = StockPriceService.get_latest_price(in_memory_db, 'AAPL')

        assert latest_price is not None
        assert latest_price.date == date(2024, 1, 2)
        assert latest_price.close_price == 188.5

    def test_get_prices_by_date_range(self, in_memory_db, sample_price_data):
        """測試根據日期範圍獲取價格"""
        # 準備數據
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')
        StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)
        in_memory_db.commit()

        # 查詢日期範圍
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 1)
        prices = StockPriceService.get_prices_by_date_range(
            in_memory_db,
            'AAPL',
            start_date,
            end_date
        )

        assert len(prices) == 1
        assert prices[0].date == date(2024, 1, 1)

    def test_delete_prices_by_symbol(self, in_memory_db, sample_price_data):
        """測試刪除股票的所有價格"""
        # 準備數據
        StockService.create_or_update_stock(in_memory_db, symbol='AAPL', name='Apple')
        StockPriceService.save_stock_prices(in_memory_db, 'AAPL', sample_price_data)
        in_memory_db.commit()

        # 刪除
        count = StockPriceService.delete_prices_by_symbol(in_memory_db, 'AAPL')

        assert count == 2

        # 驗證刪除
        prices = in_memory_db.query(StockPrice).filter_by(symbol='AAPL').all()
        assert len(prices) == 0

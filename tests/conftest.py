"""
pytest 配置和共享 fixtures
"""

import sys
import os
import pytest
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture(scope="session")
def test_config():
    """測試配置"""
    return {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'stocks_data_test',
            'user': 'test_user',
            'password': 'test_password'
        },
        'api': {
            'host': '127.0.0.1',
            'port': 8001
        }
    }


@pytest.fixture
def mock_yahoo_data():
    """模擬 Yahoo Finance 數據"""
    return {
        'AAPL': {
            'info': {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'exchange': 'NMS',
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            },
            'history': [
                {
                    'date': '2024-01-01',
                    'open': 185.5,
                    'high': 188.0,
                    'low': 184.5,
                    'close': 187.0,
                    'volume': 50000000,
                    'adj_close': 187.0
                }
            ]
        },
        'MSFT': {
            'info': {
                'symbol': 'MSFT',
                'name': 'Microsoft Corporation',
                'exchange': 'NMS',
                'sector': 'Technology',
                'industry': 'Software'
            },
            'history': [
                {
                    'date': '2024-01-01',
                    'open': 370.0,
                    'high': 375.0,
                    'low': 368.0,
                    'close': 373.5,
                    'volume': 20000000,
                    'adj_close': 373.5
                }
            ]
        }
    }


@pytest.fixture
def sample_stocks_data():
    """樣本股票數據"""
    return [
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'exchange': 'NMS',
            'sector': 'Technology'
        },
        {
            'symbol': 'MSFT',
            'name': 'Microsoft Corporation',
            'exchange': 'NMS',
            'sector': 'Technology'
        },
        {
            'symbol': 'GOOGL',
            'name': 'Alphabet Inc.',
            'exchange': 'NMS',
            'sector': 'Technology'
        }
    ]


@pytest.fixture
def sample_price_data():
    """樣本價格數據"""
    from datetime import date

    return [
        {
            'symbol': 'AAPL',
            'date': date(2024, 1, 1),
            'open_price': 185.5,
            'high_price': 188.0,
            'low_price': 184.5,
            'close_price': 187.0,
            'volume': 50000000,
            'adj_close_price': 187.0
        },
        {
            'symbol': 'AAPL',
            'date': date(2024, 1, 2),
            'open_price': 187.5,
            'high_price': 189.0,
            'low_price': 186.0,
            'close_price': 188.5,
            'volume': 45000000,
            'adj_close_price': 188.5
        }
    ]


@pytest.fixture
def temp_db_path(tmp_path):
    """臨時數據庫路徑"""
    return tmp_path / "test.db"

"""
API Models for FastAPI
Request and Response schemas for RESTful API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class StockResponse(BaseModel):
    """Stock information response"""
    id: int
    symbol: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockPriceResponse(BaseModel):
    """Stock price data response"""
    id: int
    symbol: str
    date: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    adj_close: Optional[float] = None
    volume: int
    created_at: datetime

    class Config:
        from_attributes = True


class StockPriceSummary(BaseModel):
    """Stock price summary for list views"""
    symbol: str
    date: datetime
    close_price: float
    volume: int


class HistoricalDataRequest(BaseModel):
    """Request model for fetching historical data"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    start_date: Optional[date] = Field(None, description="Start date (default: from config)")
    end_date: Optional[date] = Field(None, description="End date (default: today)")


class DailyDataRequest(BaseModel):
    """Request model for fetching daily data"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")


class BatchRequest(BaseModel):
    """Request model for batch operations"""
    symbols: List[str] = Field(..., description="List of stock symbols")


# ==================== Database Query Models ====================

class StockQueryRequest(BaseModel):
    """Request model for querying stock data from database"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    include_info: bool = Field(True, description="Whether to include stock basic info")
    include_prices: bool = Field(True, description="Whether to include price data")
    start_date: Optional[date] = Field(None, description="Start date for price data")
    end_date: Optional[date] = Field(None, description="End date for price data")
    limit: Optional[int] = Field(100, description="Maximum number of price records to return")


class StockQueryResponse(BaseModel):
    """Response for stock data query from database"""
    symbol: str
    found: bool
    stock_info: Optional[StockResponse] = None
    prices: List[StockPriceResponse] = []
    total_price_records: int = 0
    message: Optional[str] = None


# ==================== Yahoo Fetch Models ====================

class YahooFetchRequest(BaseModel):
    """Request model for fetching data from Yahoo Finance"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    fetch_info: bool = Field(True, description="Whether to fetch stock basic info")
    fetch_historical: bool = Field(True, description="Whether to fetch historical price data")
    start_date: Optional[date] = Field(None, description="Start date for historical data (default: 1 year ago)")
    end_date: Optional[date] = Field(None, description="End date for historical data (default: today)")


class YahooFetchResponse(BaseModel):
    """Response for Yahoo Finance data fetch operation"""
    symbol: str
    success: bool
    info_fetched: bool = False
    historical_fetched: bool = False
    records_count: int = 0
    message: Optional[str] = None
    error: Optional[str] = None


# ==================== Legacy Models (for backward compatibility) ====================

class StockDataRequest(BaseModel):
    """Legacy request model for backward compatibility"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    start_date: Optional[date] = Field(None, description="Start date for historical data (default: 1 year ago)")
    end_date: Optional[date] = Field(None, description="End date for historical data (default: today)")
    include_info: bool = Field(True, description="Whether to fetch stock basic info")
    include_historical: bool = Field(True, description="Whether to fetch historical price data")


class StockDataResponse(BaseModel):
    """Legacy response model for backward compatibility"""
    symbol: str
    success: bool
    info_fetched: bool = False
    historical_fetched: bool = False
    records_count: int = 0
    message: Optional[str] = None
    error: Optional[str] = None


class FetchHistoryResponse(BaseModel):
    """Response for historical data fetch operation"""
    symbol: str
    success: bool
    records_count: int = 0
    message: Optional[str] = None


class FetchDailyResponse(BaseModel):
    """Response for daily data fetch operation"""
    symbol: str
    success: bool
    message: Optional[str] = None


class BatchFetchResponse(BaseModel):
    """Response for batch fetch operations"""
    results: List[FetchHistoryResponse]
    total: int
    successful: int
    failed: int


class QueryParams(BaseModel):
    """Query parameters for stock price queries"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class DataFetchLogResponse(BaseModel):
    """Data fetch log response"""
    id: int
    symbol: Optional[str] = None
    fetch_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    records_count: int
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None

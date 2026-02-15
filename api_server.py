"""
Stock Data RESTful API Server
Provides RESTful endpoints with Swagger documentation
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from uvicorn import run

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.database.services import StockService, StockPriceService, DataFetchLogService
from src.data_fetcher.data_service import DataFetchService
from src.api_models import (
    StockResponse, StockPriceResponse, StockPriceSummary,
    HistoricalDataRequest, DailyDataRequest, BatchRequest,
    FetchHistoryResponse, FetchDailyResponse, BatchFetchResponse,
    StockDataRequest, StockDataResponse,
    StockQueryRequest, StockQueryResponse,
    YahooFetchRequest, YahooFetchResponse,
    QueryParams, DataFetchLogResponse, HealthResponse, ErrorResponse
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Data API",
    description="RESTful API for fetching and managing stock data from Yahoo Finance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Initialize data fetch service
data_service = DataFetchService()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing Stock Data API...")

        # Test database connection
        if not db_manager.test_connection():
            raise Exception("Database connection failed")

        # Initialize database engine
        db_manager.initialize_engine()

        # Create database tables
        db_manager.create_tables()

        logger.info("Stock Data API initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        db_manager.close()
        logger.info("API shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ==================== Health & Status Endpoints ====================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns API and database status
    """
    try:
        db_status = "connected" if db_manager.test_connection() else "disconnected"
        return HealthResponse(
            status="healthy",
            database=db_status,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    Returns API information and links to documentation
    """
    return {
        "message": "Stock Data API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# ==================== Stock Information Endpoints ====================

@app.get("/api/v1/stocks", response_model=List[StockResponse], tags=["Stocks"])
async def get_all_stocks(
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    active_only: bool = Query(True, description="Return only active stocks")
):
    """
    Get all stocks

    Retrieves a list of all stocks in the database.
    Can filter by exchange and active status.
    """
    try:
        with db_manager.session_scope() as session:
            if exchange:
                stocks = StockService.get_stocks_by_exchange(session, exchange)
                if active_only:
                    stocks = [s for s in stocks if s.is_active]
            else:
                if active_only:
                    stocks = StockService.get_all_active_stocks(session)
                else:
                    stocks = session.query(StockService.__bases__[0]).all()

            return stocks
    except Exception as e:
        logger.error(f"Error fetching stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stocks/{symbol}", response_model=StockResponse, tags=["Stocks"])
async def get_stock(symbol: str):
    """
    Get stock by symbol

    Retrieves detailed information for a specific stock.
    """
    try:
        with db_manager.session_scope() as session:
            stock = StockService.get_stock_by_symbol(session, symbol.upper())
            if not stock:
                raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
            return stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/stocks/{symbol}/update", response_model=FetchDailyResponse, tags=["Stocks"])
async def update_stock_info(symbol: str, background_tasks: BackgroundTasks):
    """
    Update stock information

    Fetches and updates basic information for the specified stock from Yahoo Finance.
    This operation runs in the background.
    """
    def fetch_info():
        try:
            success = data_service.fetch_and_store_stock_info(symbol.upper())
            if not success:
                logger.error(f"Failed to update stock info for {symbol}")
        except Exception as e:
            logger.error(f"Error updating stock info {symbol}: {e}")

    background_tasks.add_task(fetch_info)

    return FetchDailyResponse(
        symbol=symbol.upper(),
        success=True,
        message="Stock info update task started in background"
    )


# ==================== Stock Price Endpoints ====================

@app.get("/api/v1/stocks/{symbol}/prices", response_model=List[StockPriceResponse], tags=["Prices"])
async def get_stock_prices(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date (format: YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (format: YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records")
):
    """
    Get stock prices

    Retrieves price data for a specific stock.
    Can filter by date range.
    """
    try:
        with db_manager.session_scope() as session:
            symbol_upper = symbol.upper()

            if start_date and end_date:
                # Get prices by date range
                prices = StockPriceService.get_prices_by_date_range(
                    session, symbol_upper, start_date, end_date
                )
            elif start_date:
                # Get prices from start_date to latest
                prices = StockPriceService.get_prices_by_date_range(
                    session, symbol_upper, start_date, date.today()
                )
            else:
                # Get latest prices
                latest = StockPriceService.get_latest_price(session, symbol_upper)
                prices = [latest] if latest else []

            # Apply limit
            prices = prices[:limit]
            return prices
    except Exception as e:
        logger.error(f"Error fetching prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stocks/{symbol}/prices/latest", response_model=StockPriceResponse, tags=["Prices"])
async def get_latest_price(symbol: str):
    """
    Get latest stock price

    Retrieves the most recent price data for a specific stock.
    """
    try:
        with db_manager.session_scope() as session:
            price = StockPriceService.get_latest_price(session, symbol.upper())
            if not price:
                raise HTTPException(
                    status_code=404,
                    detail=f"No price data found for stock {symbol}"
                )
            return price
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/prices/batch", response_model=List[StockPriceResponse], tags=["Prices"])
async def get_batch_prices(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    start_date: Optional[date] = Query(None, description="Start date (format: YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (format: YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records")
):
    """
    Get prices for multiple stocks

    Retrieves price data for multiple stocks at once.
    """
    try:
        with db_manager.session_scope() as session:
            symbols_upper = [s.upper() for s in symbols]
            prices = StockPriceService.get_prices_by_symbols(
                session, symbols_upper, start_date, end_date
            )
            return prices[:limit]
    except Exception as e:
        logger.error(f"Error fetching batch prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Database Query Endpoints ====================

@app.post("/api/v1/query/stock", response_model=StockQueryResponse, tags=["Database Query"])
async def query_stock_data(request: StockQueryRequest):
    """
    Query stock data from database
    
    Retrieves stock information and price data from the local database.
    Does not fetch data from external sources.
    """
    try:
        symbol = request.symbol.upper()
        stock_info = None
        prices = []
        
        with db_manager.session_scope() as session:
            # 查詢股票基本信息
            if request.include_info:
                stock_service = StockService()
                stock = stock_service.get_stock_by_symbol(session, symbol)
                if stock:
                    stock_info = StockResponse.from_orm(stock)
            
            # 查詢價格資料
            if request.include_prices:
                price_service = StockPriceService()
                if request.start_date and request.end_date:
                    prices = price_service.get_prices_by_date_range(
                        session, symbol, request.start_date, request.end_date
                    )
                elif request.start_date:
                    prices = price_service.get_prices_by_date_range(
                        session, symbol, request.start_date, date.today()
                    )
                else:
                    # 獲取最新價格
                    latest = price_service.get_latest_price(session, symbol)
                    prices = [latest] if latest else []
                
                # 應用限制
                prices = prices[:request.limit]
            
            # 轉換為響應模型
            price_responses = [StockPriceResponse.from_orm(price) for price in prices]
            
            found = stock_info is not None or len(price_responses) > 0
            
            return StockQueryResponse(
                symbol=symbol,
                found=found,
                stock_info=stock_info,
                prices=price_responses,
                total_price_records=len(price_responses),
                message=f"Found data for {symbol}" if found else f"No data found for {symbol}"
            )
            
    except Exception as e:
        logger.error(f"Error querying stock data for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Fetching Endpoints ====================

@app.post("/api/v1/fetch/yahoo", response_model=YahooFetchResponse, tags=["Data Fetch"])
async def fetch_from_yahoo(request: YahooFetchRequest):
    """
    Fetch stock data from Yahoo Finance and store in database
    
    Retrieves stock information and historical price data from Yahoo Finance API
    and stores them in the local database.
    """
    try:
        symbol = request.symbol.upper()
        info_success = False
        historical_success = False
        records_count = 0
        error_message = None
        
        # 計算默認日期範圍（過去1年）
        from datetime import timedelta
        if not request.start_date:
            start_date = (datetime.now() - timedelta(days=365)).date()
        else:
            start_date = request.start_date
            
        if not request.end_date:
            end_date = datetime.now().date()
        else:
            end_date = request.end_date
        
        # 獲取股票基本信息
        if request.fetch_info:
            try:
                info_success = data_service.fetch_and_store_stock_info(symbol)
                if not info_success:
                    error_message = f"Failed to fetch stock info for {symbol}"
            except Exception as e:
                error_message = f"Error fetching stock info: {str(e)}"
                logger.error(f"Error fetching stock info for {symbol}: {e}")
        
        # 獲取歷史價格數據
        if request.fetch_historical and not error_message:
            try:
                start_str = start_date.isoformat()
                end_str = end_date.isoformat()
                historical_success, records_count = data_service.fetch_and_store_historical_data(
                    symbol, start_str, end_str
                )
                if not historical_success:
                    if not error_message:
                        error_message = f"Failed to fetch historical data for {symbol}"
            except Exception as e:
                error_message = f"Error fetching historical data: {str(e)}"
                logger.error(f"Error fetching historical data for {symbol}: {e}")
        
        # 判斷整體成功狀態
        overall_success = (info_success or not request.fetch_info) and \
                         (historical_success or not request.fetch_historical)
        
        return YahooFetchResponse(
            symbol=symbol,
            success=overall_success,
            info_fetched=info_success,
            historical_fetched=historical_success,
            records_count=records_count,
            message=f"Yahoo data fetch completed for {symbol}",
            error=error_message
        )
        
    except Exception as e:
        logger.error(f"Error in fetch_from_yahoo: {e}")
        return YahooFetchResponse(
            symbol=request.symbol.upper(),
            success=False,
            info_fetched=False,
            historical_fetched=False,
            records_count=0,
            error=f"Unexpected error: {str(e)}"
        )


@app.post("/api/v1/fetch/historical", response_model=FetchHistoryResponse, tags=["Data Fetch"])
async def fetch_historical_data(
    request: HistoricalDataRequest,
    background_tasks: BackgroundTasks
):
    """
    Fetch historical stock data

    Fetches historical price data from Yahoo Finance for the specified stock.
    This operation runs in the background.
    """
    def fetch_history():
        try:
            start_str = request.start_date.isoformat() if request.start_date else None
            end_str = request.end_date.isoformat() if request.end_date else None
            data_service.fetch_and_store_historical_data(
                request.symbol.upper(),
                start_str,
                end_str
            )
        except Exception as e:
            logger.error(f"Error fetching historical data for {request.symbol}: {e}")

    background_tasks.add_task(fetch_history)

    return FetchHistoryResponse(
        symbol=request.symbol.upper(),
        success=True,
        records_count=0,
        message="Historical data fetch task started in background"
    )


# ==================== Legacy Endpoint (for backward compatibility) ====================

@app.post("/api/v1/fetch/stock", response_model=StockDataResponse, tags=["Data Fetch"])
async def fetch_complete_stock_data_legacy(request: StockDataRequest):
    """
    Legacy endpoint for fetching complete stock data (info + historical)
    
    DEPRECATED: Use /api/v1/fetch/yahoo instead.
    Fetches both stock basic information and historical price data from Yahoo Finance.
    This operation runs synchronously and returns the actual results.
    """
    try:
        symbol = request.symbol.upper()
        info_success = False
        historical_success = False
        records_count = 0
        error_message = None
        
        # 計算默認日期範圍（過去1年）
        from datetime import timedelta
        if not request.start_date:
            start_date = (datetime.now() - timedelta(days=365)).date()
        else:
            start_date = request.start_date
            
        if not request.end_date:
            end_date = datetime.now().date()
        else:
            end_date = request.end_date
        
        # 獲取股票基本信息
        if request.include_info:
            try:
                info_success = data_service.fetch_and_store_stock_info(symbol)
                if not info_success:
                    error_message = f"Failed to fetch stock info for {symbol}"
            except Exception as e:
                error_message = f"Error fetching stock info: {str(e)}"
                logger.error(f"Error fetching stock info for {symbol}: {e}")
        
        # 獲取歷史價格數據
        if request.include_historical and not error_message:
            try:
                start_str = start_date.isoformat()
                end_str = end_date.isoformat()
                historical_success, records_count = data_service.fetch_and_store_historical_data(
                    symbol, start_str, end_str
                )
                if not historical_success:
                    if not error_message:
                        error_message = f"Failed to fetch historical data for {symbol}"
            except Exception as e:
                error_message = f"Error fetching historical data: {str(e)}"
                logger.error(f"Error fetching historical data for {symbol}: {e}")
        
        # 判斷整體成功狀態
        overall_success = (info_success or not request.include_info) and \
                         (historical_success or not request.include_historical)
        
        return StockDataResponse(
            symbol=symbol,
            success=overall_success,
            info_fetched=info_success,
            historical_fetched=historical_success,
            records_count=records_count,
            message=f"Stock data fetch completed for {symbol}",
            error=error_message
        )
        
    except Exception as e:
        logger.error(f"Error in fetch_complete_stock_data_legacy: {e}")
        return StockDataResponse(
            symbol=request.symbol.upper(),
            success=False,
            info_fetched=False,
            historical_fetched=False,
            records_count=0,
            error=f"Unexpected error: {str(e)}"
        )


@app.post("/api/v1/fetch/daily", response_model=FetchDailyResponse, tags=["Data Fetch"])
async def fetch_daily_data(
    request: DailyDataRequest,
    background_tasks: BackgroundTasks
):
    """
    Fetch daily stock data

    Fetches the latest daily price data from Yahoo Finance for the specified stock.
    This operation runs in the background.
    """
    def fetch_daily():
        try:
            data_service.fetch_and_store_daily_data(request.symbol.upper())
        except Exception as e:
            logger.error(f"Error fetching daily data for {request.symbol}: {e}")

    background_tasks.add_task(fetch_daily)

    return FetchDailyResponse(
        symbol=request.symbol.upper(),
        success=True,
        message="Daily data fetch task started in background"
    )


@app.post("/api/v1/fetch/batch-historical", response_model=BatchFetchResponse, tags=["Data Fetch"])
async def fetch_batch_historical(
    request: BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Fetch historical data for multiple stocks

    Fetches historical data for all specified stocks.
    This operation runs in the background.
    """
    def fetch_all():
        try:
            symbols_upper = [s.upper() for s in request.symbols]
            for symbol in symbols_upper:
                try:
                    data_service.fetch_and_store_historical_data(symbol)
                except Exception as e:
                    logger.error(f"Error fetching historical data for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error in batch historical fetch: {e}")

    background_tasks.add_task(fetch_all)

    return BatchFetchResponse(
        results=[
            FetchHistoryResponse(
                symbol=s.upper(),
                success=True,
                message="Historical data fetch task started in background"
            )
            for s in request.symbols
        ],
        total=len(request.symbols),
        successful=len(request.symbols),
        failed=0
    )


@app.post("/api/v1/fetch/batch-daily", response_model=BatchFetchResponse, tags=["Data Fetch"])
async def fetch_batch_daily(
    request: BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Fetch daily data for multiple stocks

    Fetches the latest daily data for all specified stocks.
    This operation runs in the background.
    """
    def fetch_all():
        try:
            symbols_upper = [s.upper() for s in request.symbols]
            for symbol in symbols_upper:
                try:
                    data_service.fetch_and_store_daily_data(symbol)
                except Exception as e:
                    logger.error(f"Error fetching daily data for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error in batch daily fetch: {e}")

    background_tasks.add_task(fetch_all)

    return BatchFetchResponse(
        results=[
            FetchHistoryResponse(
                symbol=s.upper(),
                success=True,
                message="Daily data fetch task started in background"
            )
            for s in request.symbols
        ],
        total=len(request.symbols),
        successful=len(request.symbols),
        failed=0
    )


@app.post("/api/v1/fetch/all-historical", response_model=BatchFetchResponse, tags=["Data Fetch"])
async def fetch_all_configured_historical(background_tasks: BackgroundTasks):
    """
    Fetch historical data for all configured stocks

    Fetches historical data for all stocks configured in config.yaml.
    This operation runs in the background.
    """
    def fetch_all():
        try:
            data_service.fetch_all_stocks_historical()
        except Exception as e:
            logger.error(f"Error fetching all historical data: {e}")

    background_tasks.add_task(fetch_all)

    symbols = config.get('yahoo_finance.symbols', [])
    return BatchFetchResponse(
        results=[
            FetchHistoryResponse(
                symbol=s,
                success=True,
                message="Historical data fetch task started in background"
            )
            for s in symbols
        ],
        total=len(symbols),
        successful=len(symbols),
        failed=0
    )


@app.post("/api/v1/fetch/all-daily", response_model=BatchFetchResponse, tags=["Data Fetch"])
async def fetch_all_configured_daily(background_tasks: BackgroundTasks):
    """
    Fetch daily data for all configured stocks

    Fetches the latest daily data for all stocks configured in config.yaml.
    This operation runs in the background.
    """
    def fetch_all():
        try:
            data_service.fetch_all_stocks_daily()
        except Exception as e:
            logger.error(f"Error fetching all daily data: {e}")

    background_tasks.add_task(fetch_all)

    symbols = config.get('yahoo_finance.symbols', [])
    return BatchFetchResponse(
        results=[
            FetchHistoryResponse(
                symbol=s,
                success=True,
                message="Daily data fetch task started in background"
            )
            for s in symbols
        ],
        total=len(symbols),
        successful=len(symbols),
        failed=0
    )


# ==================== Logs Endpoints ====================

@app.get("/api/v1/logs", response_model=List[DataFetchLogResponse], tags=["Logs"])
async def get_fetch_logs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of log entries"),
    status: Optional[str] = Query(None, description="Filter by status (success/failed/partial)")
):
    """
    Get data fetch logs

    Retrieves recent data fetch operation logs.
    """
    try:
        with db_manager.session_scope() as session:
            logs = DataFetchLogService.get_recent_logs(session, limit, status)
            return logs
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


def main():
    """Run the API server"""
    host = config.get('api.host', '0.0.0.0')
    port = config.get('api.port', 8000)

    logger.info(f"Starting Stock Data API on {host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")

    run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == '__main__':
    main()

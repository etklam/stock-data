# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive stock data management system that fetches stock market data from Yahoo Finance, stores it in PostgreSQL, and provides both CLI and RESTful API interfaces. The system supports multi-dimensional stock categorization (industry, region, market cap), automated data fetching via scheduled tasks, and batch processing.

## Tech Stack

- **Python 3.8+**
- **FastAPI** for RESTful API with automatic OpenAPI/Swagger documentation
- **PostgreSQL** with SQLAlchemy ORM and connection pooling
- **yfinance** library for Yahoo Finance API integration
- **APScheduler** for automated scheduled data fetching
- **Pandas** for data manipulation
- **YAML-based configuration** with `src/config/config_manager.py`

## Common Commands

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment variables for sensitive data
cp .env.example .env
# Edit .env with your database credentials and other sensitive settings
# The system will load .env and override config.yaml values automatically
```

### CLI Mode (main.py)
```bash
# Initialize database and create tables
python main.py --init

# Fetch historical data for all configured stocks
python main.py --historical

# Fetch historical data for specific stocks
python main.py --historical AAPL MSFT

# Fetch daily/latest data for all stocks
python main.py --daily

# Fetch daily data for specific stocks
python main.py --daily AAPL MSFT

# Update stock information (name, exchange, sector, etc.)
python main.py --update-info

# Run as daemon (starts scheduler for automated tasks)
python main.py --daemon
```

### API Server (api_server.py)
```bash
# Start API server (simple)
python run_api.py

# Start with uvicorn directly
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# Start with multiple workers
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Architecture

### Entry Points

1. **main.py** - CLI application
   - Implements `StockDataSystem` class orchestrating all operations
   - Supports: initialization, historical/daily fetching, info updates, daemon mode
   - Handles signal processing for graceful shutdown (SIGINT, SIGTERM)

2. **api_server.py** - FastAPI application
   - RESTful endpoints for stock management, price retrieval, data fetching
   - Background task execution for non-blocking operations
   - Automatic OpenAPI documentation

### Core Modules

**Configuration** (`src/config/`)
- `config_manager.py`: Centralized YAML configuration manager
- Supports dot notation access: `config.get('database.host')`
- Reads from `config.yaml` for database, API, scheduler, and categorization settings

**Database Layer** (`src/database/`)
- `connection.py`: `DatabaseManager` class with SQLAlchemy engine, connection pooling, session management
  - Connection pool: 10 base connections, 20 max overflow
  - `session_scope()` context manager for transaction handling
  - Raw SQL execution support via psycopg2
- `models.py`: SQLAlchemy ORM models (Stock, StockPrice, DataFetchLog, StockCategory, StockCategoryMapping, SystemConfig)
- `services.py`: Service classes for each model (StockService, StockPriceService, etc.)

**Data Fetching** (`src/data_fetcher/`)
- `yahoo_client.py`: Yahoo Finance API client with retry logic and rate limiting
- `data_service.py`: Integration layer coordinating API client and database, handles data transformation and validation

**Scheduler** (`src/scheduler/task_scheduler.py`)
- APScheduler-based task scheduling
- Built-in tasks: daily data fetch (default 18:00), hourly missing data check, weekly info updates
- Supports custom job management

**Utilities** (`src/utils/`)
- `logger.py`: Structured logging with rotation (10MB max, 5 backups)

**API Models** (`src/api_models.py`)
- Pydantic models for request/response validation

### Database Models

- **Stock**: Basic stock info (symbol, name, exchange, sector, industry, is_active)
- **StockPrice**: Historical price data (symbol, date, open_price, high_price, low_price, close_price, volume, adj_close_price)
- **StockCategory**: Category definitions (name, type, description, parent_id for hierarchy)
- **StockCategoryMapping**: Stock-to-category relationships (symbol, category_id, is_primary)
- **DataFetchLog**: Operation logs (symbol, fetch_type, status, records_count, error_message, timestamp)
- **SystemConfig**: Key-value configuration storage

### Stock Categorization System

Stocks can be categorized in multiple dimensions (configured in `config.yaml`):
- **industry**: technology, healthcare, finance, consumer, energy
- **region**: us_market, taiwan_market, etc.
- **market_cap**: large_cap, mid_cap, small_cap
- **custom**: User-defined categories

The system maintains category mappings in `stock_category_mappings` table, allowing stocks to belong to multiple categories simultaneously.

## Configuration Files

The configuration system supports both `config.yaml` (default settings) and `.env` (environment variable overrides for sensitive data).

### config.yaml (Default Configuration)
Primary configuration file with default values. Key sections:
- `database`: PostgreSQL connection settings (use placeholder for password)
- `yahoo_finance`: Stock symbols, categories, fetch interval, start date
- `scheduler`: Task scheduling settings (daily_fetch_time, enabled status)
- `logging`: Log level, format, file rotation
- `api`: API server host/port, reload, workers

**Best practice**: Keep non-sensitive defaults here, use placeholders for secrets.

### .env (Environment Variables - Overrides)
Environment variables **override** config.yaml values. Essential for sensitive data:
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- `API_HOST`, `API_PORT`, `API_RELOAD`, `API_WORKERS`
- Other optional overrides: `YAHOO_FETCH_INTERVAL`, `SCHEDULER_ENABLED`, `LOG_LEVEL`, etc.

**Security**: `.env` is in `.gitignore` and never committed to version control.

### Environment Variable Mapping
The `ConfigManager` automatically maps environment variables to config paths:
- `DATABASE_PASSWORD` → `database.password`
- `API_HOST` → `api.host`
- `SCHEDULER_ENABLED` → `scheduler.enabled`
- See `src/config/config_manager.py` `ENV_MAPPING` for complete list

Values are automatically converted to appropriate types (bool, int, float, str).

## Database Setup

```sql
CREATE DATABASE stocks_data;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stocks_data TO your_username;
```

## Key Patterns

1. **Service Layer**: Business logic in service classes (StockService, StockPriceService, etc.)
2. **Context Managers**: Always use `db_manager.session_scope()` for database transactions
3. **Error Handling**: Comprehensive logging at all levels, retry mechanisms in API client
4. **Batch Operations**: Use batch methods for fetching multiple stocks to avoid API rate limits
5. **Background Tasks**: API endpoints use `BackgroundTasks` for long-running operations

## Important Notes

- Stock symbols use Yahoo Finance format (e.g., "AAPL", "2330.TW" for Taiwan stocks)
- The system automatically creates database tables on first run via `--init`
- Daemon mode requires scheduler to be enabled in config
- All timestamps stored in UTC
- Connection pooling prevents connection exhaustion; adjust pool_size in `connection.py` if needed
- API endpoints return JSON responses with appropriate HTTP status codes
- Scheduled tasks only run when daemon mode is active

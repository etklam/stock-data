# 股票數據獲取系統

一個使用 Python 和 Yahoo Finance API 的股票數據獲取系統，支持歷史數據獲取、每日定時存儲到 PostgreSQL 數據庫，以及 RESTful API 服務。

## 📑 目錄

- [功能特性](#功能特性)
- [系統架構](#系統架構)
- [安裝和配置](#安裝和配置)
- [使用方式](#使用方式)
  - [CLI 模式](#cli-模式)
  - [API 模式](#api-模式)
- [CLI 使用指南](#cli-使用指南)
- [RESTful API 使用指南](#restful-api-使用指南)
  - [🔍 資料庫查詢API](#-資料庫查詢api)
  - [🌐 Yahoo獲取API](#-yahoo獲取api)
  - [API端點總覽](#api端點總覽)
- [定時任務](#定時任務)
- [股票分類系統](#股票分類系統)
- [數據庫結構](#數據庫結構)
- [日誌系統](#日誌系統)
- [常見問題](#常見問題)

## 功能特性

- 📈 從 Yahoo Finance 獲取股票歷史數據和實時數據
- 🗄️ 使用 PostgreSQL 存儲股票數據
- 🔍 **雙層API架構**：資料庫查詢API + Yahoo獲取API
- 🏷️ **多維度股票分類系統**（按行業、地區、市值等分類）
- ⏰ 支持定時任務，自動獲取每日數據
- 🚀 RESTful API with OpenAPI/Swagger 文檔
- 🔧 靈活的配置管理
- 📝 完整的日誌記錄
- 🛡️ 錯誤處理和重試機制
- 📊 數據完整性檢查

## 系統架構

```
stocks-data/
├── src/                    # 源代碼目錄
│   ├── config/            # 配置管理模塊
│   ├── database/          # 數據庫操作模塊
│   ├── data_fetcher/      # 數據獲取模塊
│   ├── scheduler/         # 任務調度模塊
│   └── utils/             # 工具模塊
├── scripts/               # 腳本目錄
│   ├── fetch_aapl_data.py    # AAPL數據獲取範例
│   ├── api_fetch_example.py   # API使用範例
│   └── new_api_example.py    # 新API結構範例
├── logs/                  # 日誌目錄
├── data/                  # 數據目錄
├── venv/                  # Python 虛擬環境
├── config.yaml            # 配置文件
├── requirements.txt       # Python 依賴
├── .env.example           # 環境變數範例
├── .env                   # 環境變數配置
├── main.py               # 統一程序入口
├── api_server.py         # RESTful API 服務器
├── run_api.py           # API 啟動腳本（相容層）
├── API_USAGE_GUIDE.md    # API使用指南
└── NEW_API_STRUCTURE_GUIDE.md # 新API結構指南
```

### 系統組件

- **CLI 工具** (`main.py`) - 命令行界面，用於一次性數據獲取和定時任務
- **API 服務器** (`api_server.py`) - RESTful API 服務，帶 Swagger 文檔
- **數據獲取器** - 從 Yahoo Finance 獲取股票數據
- **數據庫層** - PostgreSQL 數據存儲和查詢
- **調度器** - 定時任務管理（可選）

## 安裝和配置

### 1. 環境要求

- Python 3.8+
- PostgreSQL 12+
- pip

### 2. 設置虛擬環境

為確保項目依賴隔離，建議使用 Python 虛擬環境：

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/macOS
# 或者在 Windows 上使用
# venv\Scripts\activate
```

### 3. 配置環境變數

複製環境變數範例文件並根據需要修改：

```bash
cp .env.example .env
```

編輯 `.env` 文件，配置數據庫連接和其他設置。

### 4. 安裝依賴

在虛擬環境中安裝所有依賴：

```bash
pip install -r requirements.txt
```

### 5. 數據庫設置

創建 PostgreSQL 數據庫：

```sql
CREATE DATABASE stocks_data;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stocks_data TO your_username;
```

### 6. 配置文件

編輯 `config.yaml` 文件，配置數據庫連接和股票列表：

```yaml
# 數據庫配置
database:
  host: localhost
  port: 5432
  name: stocks_data
  user: postgres
  password: your_password

# Yahoo Finance 配置
yahoo_finance:
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - 2330.TW  # 台積電
    - 2317.TW  # 鴻海
  start_date: "2020-01-01"

# 調度器配置
scheduler:
  daily_fetch_time: "18:00"
  enabled: true

# API 配置
api:
  host: "0.0.0.0"
  port: 8001
  reload: false
  workers: 1
```

## 使用方式

本項目提供兩種使用方式：

1. **CLI 命令行界面** - 適合一次性數據獲取和定時任務
2. **RESTful API** - 適合集成到其他應用和 Web 服務

### CLI 模式

```bash
# 初始化數據庫
python main.py --init

# 獲取歷史數據
python main.py --historical

# 獲取每日數據
python main.py --daily

# 啟動定時任務（可選）
python main.py --daemon
```

### API 模式

```bash
# 啟動 API 服務器
python main.py api

# 指定端口
python main.py api --port 8001

# 禁用重載（生產模式）
python main.py api --no-reload

# 訪問 Swagger 文檔
open http://localhost:8001/docs
```

## CLI 使用指南

### 初始化系統

```bash
python main.py --init
```

### 獲取歷史數據

獲取所有配置股票的歷史數據：

```bash
python main.py --historical
```

獲取指定股票的歷史數據：

```bash
python main.py --historical AAPL MSFT
```

### 獲取每日數據

獲取所有股票的最新數據：

```bash
python main.py --daily
```

獲取指定股票的最新數據：

```bash
python main.py --daily AAPL MSFT
```

### 更新股票信息

更新所有股票的基本信息：

```bash
python main.py --update-info
```

更新指定股票的信息：

```bash
python main.py --update-info AAPL MSFT
```

### 啟動守護進程

以守護進程模式運行，自動執行定時任務：

```bash
python main.py --daemon
```

## RESTful API 使用指南

### 🔍 資料庫查詢API

**用途**: 從本地資料庫快速查詢已儲存的股票資料

#### 主要端點

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/v1/query/stock` | 查詢股票資料（基本信息 + 價格） |

#### 請求參數

```json
{
  "symbol": "AAPL",           // 必填：股票代碼
  "include_info": true,        // 選填：是否包含基本信息
  "include_prices": true,      // 選填：是否包含價格資料
  "start_date": "2025-01-01", // 選填：開始日期
  "end_date": "2025-12-31",   // 選填：結束日期
  "limit": 100               // 選填：最大記錄數
}
```

#### 使用範例

```bash
# 查詢AAPL的完整資料
curl -X POST "http://localhost:8001/api/v1/query/stock" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "AAPL",
  "include_info": true,
  "include_prices": true,
  "limit": 5
}'

# 只查詢指定日期範圍的價格
curl -X POST "http://localhost:8001/api/v1/query/stock" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "MSFT",
  "include_info": false,
  "include_prices": true,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}'
```

### 🌐 Yahoo獲取API

**用途**: 從Yahoo Finance獲取新資料並儲存到資料庫

#### 主要端點

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/api/v1/fetch/yahoo` | 從Yahoo獲取資料並儲存 |

#### 請求參數

```json
{
  "symbol": "AAPL",           // 必填：股票代碼
  "fetch_info": true,         // 選填：是否獲取基本信息
  "fetch_historical": true,   // 選填：是否獲取歷史資料
  "start_date": "2025-01-01", // 選填：歷史資料開始日期
  "end_date": "2025-12-31"    // 選填：歷史資料結束日期
}
```

#### 使用範例

```bash
# 獲取完整股票資料（預設過去1年）
curl -X POST "http://localhost:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "NFLX",
  "fetch_info": true,
  "fetch_historical": true
}'

# 只獲取股票基本信息
curl -X POST "http://localhost:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "DIS",
  "fetch_info": true,
  "fetch_historical": false
}'

# 獲取指定日期範圍的歷史資料
curl -X POST "http://localhost:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "NVDA",
  "fetch_info": false,
  "fetch_historical": true,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}'
```

### API端點總覽

| 類別 | 方法 | 端點 | 說明 |
|------|------|------|------|
| **Health** | GET | `/health` | 健康檢查 |
| **Database Query** | POST | `/api/v1/query/stock` | 查詢資料庫股票資料 |
| **Stocks** | GET | `/api/v1/stocks` | 獲取所有股票 |
| **Stocks** | GET | `/api/v1/stocks/{symbol}` | 獲取特定股票 |
| **Prices** | GET | `/api/v1/stocks/{symbol}/prices` | 獲取價格數據 |
| **Prices** | GET | `/api/v1/stocks/{symbol}/prices/latest` | 獲取最新價格 |
| **Data Fetch** | POST | `/api/v1/fetch/yahoo` | 從Yahoo獲取資料 |
| **Data Fetch** | POST | `/api/v1/fetch/historical` | 獲取歷史數據 |
| **Data Fetch** | POST | `/api/v1/fetch/daily` | 獲取每日數據 |
| **Logs** | GET | `/api/v1/logs` | 獲取操作日誌 |

### 推薦工作流程

1. **先查詢**: 使用 `/api/v1/query/stock` 檢查資料是否已存在
2. **後獲取**: 如需最新資料，使用 `/api/v1/fetch/yahoo` 從Yahoo更新

```python
# 推薦工作流程範例
import requests

def get_or_fetch_stock(symbol):
    # 1. 先查詢資料庫
    query_response = requests.post(
        "http://localhost:8001/api/v1/query/stock",
        json={"symbol": symbol, "include_info": True, "include_prices": True}
    )
    
    if not query_response.json()['found']:
        # 2. 如果沒有資料，從Yahoo獲取
        fetch_response = requests.post(
            "http://localhost:8001/api/v1/fetch/yahoo",
            json={"symbol": symbol, "fetch_info": True, "fetch_historical": True}
        )
        return fetch_response.json()
    
    return query_response.json()
```

### API 使用範例

#### 使用 Python requests

```python
import requests

BASE_URL = "http://localhost:8001"

# 查詢資料庫中的股票
def query_stock(symbol):
    response = requests.post(
        f"{BASE_URL}/api/v1/query/stock",
        json={
            "symbol": symbol,
            "include_info": True,
            "include_prices": True,
            "limit": 10
        }
    )
    return response.json()

# 從Yahoo獲取新資料
def fetch_stock(symbol):
    response = requests.post(
        f"{BASE_URL}/api/v1/fetch/yahoo",
        json={
            "symbol": symbol,
            "fetch_info": True,
            "fetch_historical": True
        }
    )
    return response.json()

# 使用範例
aapl_data = query_stock("AAPL")
if not aapl_data['found']:
    aapl_data = fetch_stock("AAPL")
```

## 定時任務

系統包含以下定時任務：

1. **每日數據獲取**：每天 18:00 自動獲取所有股票的最新數據
2. **缺失數據檢查**：每小時檢查一次缺失的數據並自動補充
3. **股票信息更新**：每週一 9:00 更新所有股票的基本信息

## 股票分類系統

系統支持多維度股票分類，可以根據行業、地區、市值等方式對股票進行分組管理。

### 分類類型

1. **行業分類 (industry)**
   - 科技業
   - 醫療保健
   - 金融業
   - 消費品
   - 能源業

2. **地區分類 (region)**
   - 美國市場
   - 台灣市場
   - 其他地區

3. **市值分類 (market_cap)**
   - 大型股
   - 中型股
   - 小型股

## 數據庫結構

### stocks 表
存儲股票基本信息：
- `symbol`: 股票代碼
- `name`: 股票名稱
- `exchange`: 交易所
- `sector`: 行業
- `industry`: 產業
- `market_cap`: 市值

### stock_prices 表
存儲股票價格數據：
- `symbol`: 股票代碼
- `date`: 日期
- `open_price`: 開盤價
- `high_price`: 最高價
- `low_price`: 最低價
- `close_price`: 收盤價
- `volume`: 成交量

### data_fetch_logs 表
存儲數據獲取日誌：
- `symbol`: 股票代碼
- `fetch_type`: 獲取類型
- `status`: 狀態
- `records_count`: 記錄數
- `error_message`: 錯誤信息

## 日誌系統

日誌文件位置：`logs/stocks_data.log`

日誌級別：
- INFO：一般信息
- WARNING：警告信息
- ERROR：錯誤信息
- DEBUG：調試信息

## 常見問題

### 1. 數據庫連接失敗

檢查 `config.yaml` 中的數據庫配置是否正確：

```yaml
database:
  host: localhost
  port: 5432
  name: stocks_data
  user: your_username
  password: your_password
```

### 2. 無法獲取股票數據

可能的原因：
- 股票代碼不正確
- 網絡連接問題
- Yahoo Finance API 限制

### 3. API 端點無響應

檢查API服務器是否正確啟動：

```bash
# 檢查端口是否被占用
lsof -i :8001

# 重新啟動API服務器
python main.py api --port 8001 --no-reload
```

## 性能優化

1. **數據庫索引**：系統已自動創建必要的索引
2. **批量操作**：使用批量插入提高性能
3. **連接池**：使用 SQLAlchemy 連接池
4. **API 限制**：設置合理的請求間隔

## 擴展功能

### 添加新股票

在 `config.yaml` 中添加股票代碼：

```yaml
yahoo_finance:
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - NEW_STOCK  # 新增股票
```

### 自定義定時任務

可以通過修改 `src/scheduler/task_scheduler.py` 添加自定義任務。

## 監控和維護

### 查看系統狀態

```bash
# 查看最近的日誌
tail -f logs/stocks_data.log

# 查看數據庫記錄數
python -c "
from src.database.connection import db_manager
from src.database.models import StockPrice
with db_manager.session_scope() as session:
    count = session.query(StockPrice).count()
    print(f'總記錄數: {count}')
"
```

### 數據備份

定期備份 PostgreSQL 數據庫：

```bash
pg_dump stocks_data > backup_$(date +%Y%m%d).sql
```

## 許可證

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯繫方式

如有問題，請通過以下方式聯繫：
- 提交 GitHub Issue
- 發送郵件至：your-email@example.com

## 📚 相關文檔

- [`API_USAGE_GUIDE.md`](API_USAGE_GUIDE.md) - 詳細的API使用指南
- [`NEW_API_STRUCTURE_GUIDE.md`](NEW_API_STRUCTURE_GUIDE.md) - 新API結構指南
- [`scripts/new_api_example.py`](scripts/new_api_example.py) - 新API使用範例
- [`scripts/fetch_aapl_data.py`](scripts/fetch_aapl_data.py) - AAPL數據獲取範例
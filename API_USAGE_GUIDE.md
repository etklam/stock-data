# 股票資料 API 使用指南

## 概述

本系統提供一個強大的 RESTful API，可從 Yahoo Finance 獲取股票市場資料並管理在本地的 PostgreSQL 資料庫中。API 分為兩個清晰的類別：

1. **資料庫查詢 API** - 從本地資料庫查詢已有股票資料（快速，無外部 API 呼叫）
2. **資料獲取 API** - 從 Yahoo Finance 獲取新股票資料並儲存到資料庫（較慢，外部 API 呼叫）

---

## API 架構

### 雙層 API 設計

API 結構化設計以清晰區分查詢已有資料和獲取新資料：

| API 類型 | 用途 | 速度 | 網絡依賴 | 使用場景 |
|----------|------|------|----------|----------|
| **資料庫查詢 API** | 查詢已儲存資料 | 快 | 無 | 檢索已有資料 |
| **資料獲取 API** | 獲取新資料 | 慢 | Yahoo Finance | 獲取或更新資料 |

### 推薦工作流程

```
1. 先查詢資料庫 → 檢查資料是否存在
2. 從 Yahoo 獲取（如需要）→ 更新或新增資料
3. 再次查詢 → 檢索更新後的資料
```

---

## 1. 資料庫查詢 API

### 端點：查詢股票資料

**URL**: `POST http://127.0.0.1:8001/api/v1/query/stock`

**描述**: 從本地資料庫檢索股票資訊和價格資料，不進行外部 API 呼叫。快速且高效。

### 請求參數

| 參數 | 類型 | 必填 | 描述 | 預設值 |
|------|------|------|------|--------|
| symbol | string | 是 | 股票代碼（如 "AAPL"、"MSFT"） | - |
| include_info | boolean | 否 | 包含基本股票資訊 | true |
| include_prices | boolean | 否 | 包含價格資料 | true |
| start_date | string | 否 | 價格資料開始日期 (YYYY-MM-DD) | - |
| end_date | string | 否 | 價格資料結束日期 (YYYY-MM-DD) | - |
| limit | integer | 否 | 最大價格記錄數 | 100 |

### 響應格式

```json
{
  "symbol": "AAPL",
  "found": true,
  "stock_info": {
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NMS",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": 3759435415552.0,
    "is_active": true,
    "created_at": "2026-02-15T09:23:15.598485",
    "updated_at": "2026-02-15T09:23:15.598492"
  },
  "prices": [
    {
      "id": 250,
      "symbol": "AAPL",
      "date": "2026-02-13T05:00:00",
      "open_price": 262.01,
      "high_price": 262.23,
      "low_price": 255.45,
      "close_price": 255.78,
      "adj_close": 255.78,
      "volume": 56229900,
      "created_at": "2026-02-15T09:23:34.702061"
    }
  ],
  "total_price_records": 1,
  "message": "Found data for AAPL"
}
```

### 使用範例

#### 查詢股票資訊和最新價格
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/query/stock" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "AAPL",
  "include_info": true,
  "include_prices": true,
  "limit": 5
}'
```

#### 查詢指定日期範圍的價格資料
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/query/stock" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "MSFT",
  "include_info": false,
  "include_prices": true,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}'
```

#### 只查詢股票資訊（不含價格）
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/query/stock" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "GOOGL",
  "include_info": true,
  "include_prices": false
}'
```

#### Python 範例
```python
import requests
from datetime import datetime, timedelta

def query_stock_data(symbol, start_date=None, end_date=None, limit=100):
    """從本地資料庫查詢股票資料"""
    url = "http://127.0.0.1:8001/api/v1/query/stock"

    payload = {
        "symbol": symbol,
        "include_info": True,
        "include_prices": True,
        "limit": limit
    }

    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    response = requests.post(url, json=payload)
    return response.json()

# 範例：查詢 AAPL 股票資料
result = query_stock_data("AAPL")
if result["found"]:
    print(f"股票：{result['stock_info']['name']}")
    print(f"價格記錄數：{result['total_price_records']}")
    print(f"最新價格：${result['prices'][0]['close_price']:.2f}")
else:
    print("資料庫中找不到該股票")
```

---

## 2. 資料獲取 API (Yahoo Finance)

### 端點：從 Yahoo Finance 獲取資料

**URL**: `POST http://127.0.0.1:8001/api/v1/fetch/yahoo`

**描述**: 從 Yahoo Finance API 獲取股票資訊和歷史價格資料，並儲存到本地資料庫。此操作會進行外部 API 呼叫。

### 請求參數

| 參數 | 類型 | 必填 | 描述 | 預設值 |
|------|------|------|------|--------|
| symbol | string | 是 | 股票代碼（如 "AAPL"、"MSFT"） | - |
| fetch_info | boolean | 否 | 獲取基本股票資訊 | true |
| fetch_historical | boolean | 否 | 獲取歷史價格資料 | true |
| start_date | string | 否 | 歷史資料開始日期 (YYYY-MM-DD) | 1年前 |
| end_date | string | 否 | 歷史資料結束日期 (YYYY-MM-DD) | 今天 |

### 響應格式

```json
{
  "symbol": "NFLX",
  "success": true,
  "info_fetched": true,
  "historical_fetched": true,
  "records_count": 249,
  "message": "Yahoo data fetch completed for NFLX",
  "error": null
}
```

### 使用範例

#### 獲取完整股票資料（預設：過去1年）
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "NFLX",
  "fetch_info": true,
  "fetch_historical": true
}'
```

#### 只獲取基本股票資訊
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "DIS",
  "fetch_info": true,
  "fetch_historical": false
}'
```

#### 獲取指定日期範圍的歷史資料
```bash
curl -X POST "http://127.0.0.1:8001/api/v1/fetch/yahoo" \
-H "Content-Type: application/json" \
-d '{
  "symbol": "NVDA",
  "fetch_info": false,
  "fetch_historical": true,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}'
```

#### Python 範例
```python
import requests
from datetime import datetime, timedelta

def fetch_stock_from_yahoo(symbol, fetch_info=True, fetch_historical=True,
                          start_date=None, end_date=None):
    """從 Yahoo Finance 獲取股票資料"""
    url = "http://127.0.0.1:8001/api/v1/fetch/yahoo"

    payload = {
        "symbol": symbol,
        "fetch_info": fetch_info,
        "fetch_historical": fetch_historical
    }

    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    response = requests.post(url, json=payload)
    return response.json()

# 範例：獲取 TSLA 過去一年的資料
result = fetch_stock_from_yahoo("TSLA")
if result["success"]:
    print(f"成功獲取 {result['records_count']} 條記錄")
    if result["info_fetched"]:
        print("股票資訊已更新")
    if result["historical_fetched"]:
        print("歷史資料已更新")
else:
    print(f"錯誤：{result['error']}")
```

---

## 3. 綜合工作流程範例

### 最佳實踐：先查詢後獲取

```python
import requests
from datetime import datetime, timedelta

API_BASE = "http://127.0.0.1:8001/api/v1"

def get_stock_data(symbol, force_refresh=False):
    """
    智能緩存機制獲取股票資料：
    1. 先查詢資料庫
    2. 如找不到或需要強制更新，從 Yahoo 獲取
    3. 再次查詢以返回資料
    """

    # 步驟 1：先查詢資料庫
    query_response = requests.post(
        f"{API_BASE}/query/stock",
        json={
            "symbol": symbol,
            "include_info": True,
            "include_prices": True,
            "limit": 10
        }
    )
    query_data = query_response.json()

    # 步驟 2：如需要，從 Yahoo 獲取
    if not query_data["found"] or force_refresh:
        print(f"正在從 Yahoo Finance 獲取 {symbol} 資料...")
        fetch_response = requests.post(
            f"{API_BASE}/fetch/yahoo",
            json={
                "symbol": symbol,
                "fetch_info": True,
                "fetch_historical": True
            }
        )
        fetch_data = fetch_response.json()

        if not fetch_data["success"]:
            return {"error": fetch_data["error"]}

        # 步驟 3：再次查詢以獲取資料
        query_response = requests.post(
            f"{API_BASE}/query/stock",
            json={
                "symbol": symbol,
                "include_info": True,
                "include_prices": True,
                "limit": 10
            }
        )
        query_data = query_response.json()

    return query_data

# 使用範例
data = get_stock_data("AAPL")
if "error" not in data:
    print(f"股票：{data['stock_info']['name']}")
    print(f"最新價格：${data['prices'][0]['close_price']:.2f}")
```

---

## 4. 其他可用端點

### GET 端點（股票資訊）

#### 獲取所有股票
```
GET /api/v1/stocks?exchange=NMS&active_only=true
```

#### 獲取指定股票
```
GET /api/v1/stocks/{symbol}
```

#### 更新股票資訊（後台任務）
```
POST /api/v1/stocks/{symbol}/update
```

### GET 端點（股票價格）

#### 獲取股票價格（含日期篩選）
```
GET /api/v1/stocks/{symbol}/prices?start_date=2025-01-01&end_date=2025-12-31&limit=100
```

#### 獲取最新價格
```
GET /api/v1/stocks/{symbol}/prices/latest
```

#### 批量獲取多支股票價格
```
GET /api/v1/prices/batch?symbols=AAPL&symbols=MSFT&limit=1000
```

### 批量獲取端點（後台任務）

#### 獲取歷史資料（後台執行）
```
POST /api/v1/fetch/historical
```

#### 獲取每日資料（後台執行）
```
POST /api/v1/fetch/daily
```

#### 批量獲取歷史資料（後台執行）
```
POST /api/v1/fetch/batch-historical
```

#### 批量獲取每日資料（後台執行）
```
POST /api/v1/fetch/batch-daily
```

#### 獲取所有已配置股票（後台執行）
```
POST /api/v1/fetch/all-historical
POST /api/v1/fetch/all-daily
```

### 日誌端點

#### 獲取獲取日誌
```
GET /api/v1/logs?limit=100&status=success
```

---

## 5. 錯誤處理

### 查詢 API 錯誤

如果資料庫中找不到股票資料，API 返回：
```json
{
  "symbol": "UNKNOWN",
  "found": false,
  "stock_info": null,
  "prices": [],
  "total_price_records": 0,
  "message": "No data found for UNKNOWN"
}
```

### 獲取 API 錯誤

如果 Yahoo Finance API 呼叫失敗：
```json
{
  "symbol": "INVALID",
  "success": false,
  "info_fetched": false,
  "historical_fetched": false,
  "records_count": 0,
  "message": "Yahoo data fetch completed for INVALID",
  "error": "Error fetching stock info: Stock symbol not found"
}
```

---

## 6. 重要注意事項

### 股票代碼格式
- 使用大寫字母："AAPL"、"MSFT"、"GOOGL"
- 台灣股票："2330.TW"
- 其他市場：請查閱 Yahoo Finance 確認正確後綴

### 日期格式
- 使用 ISO 8601 格式：YYYY-MM-DD
- 時區：所有時間以 UTC 儲存

### 預設日期範圍
- 如未指定，獲取 API 預設為過去 1 年
- 查詢 API 返回所有可用資料（受限制參數約束）

### 頻率限制
- Yahoo Finance 有 API 呼叫頻率限制
- 盡可能使用批量端點處理多支股票
- 實施適當的錯誤處理和重試邏輯

### 資料儲存
- 所有資料儲存在 PostgreSQL 資料庫
- 資料表：`stocks`、`stock_prices`、`data_fetch_logs`
- 自動重複處理（upsert 操作）

---

## 7. 範例腳本

參考以下腳本獲取完整的使用範例：
- [`scripts/new_api_example.py`](scripts/new_api_example.py) - 新 API 結構範例
- [`scripts/api_fetch_example.py`](scripts/api_fetch_example.py) - 獲取 API 範例
- [`scripts/fetch_aapl_data.py`](scripts/fetch_aapl_data.py) - 完整工作流程範例

---

## 8. 互動式 API 文檔

啟動 API 伺服器後，存取互動式文檔：

### Swagger UI（推薦）
```
http://127.0.0.1:8001/docs
```
- 直接測試端點
- 檢視請求/響應架構
- 使用不同參數測試

### ReDoc
```
http://127.0.0.1:8001/redoc
```
- 唯讀文檔
- 適合列印/參考

### 健康檢查
```
http://127.0.0.1:8001/health
```

---

## 9. API 版本與相容性

### 目前版本：v1.0

### 新結構（推薦）
- `POST /api/v1/query/stock` - 資料庫查詢 API
- `POST /api/v1/fetch/yahoo` - Yahoo Finance 獲取 API

### 舊端點（已棄用）
- `POST /api/v1/fetch/stock` - 標記為已棄用，但仍可使用

### 遷移指南
如果您正在使用舊的 `/api/v1/fetch/stock` 端點：
1. 使用 `/api/v1/fetch/yahoo` 進行資料獲取
2. 使用 `/api/v1/query/stock` 查詢已有資料

---

## 10. 支援的股票

理論上支援所有 Yahoo Finance 提供的股票：

### 美國股票
- 科技股：AAPL、MSFT、GOOGL、META、NVDA、TSLA
- 醫療股：JNJ、PFE、UNH
- 金融股：JPM、BAC、WFC
- 消費股：AMZN、COST、HD
- 能源股：XOM、CVX、COP

### 其他市場
- 台灣：2330.TW（台積電）、2454.TW（聯發科）
- 日本：7203.T（Toyota）、6758.T（Sony）
- 以及更多 - 請查閱 Yahoo Finance 確認代碼

---

## 快速參考

### 查詢資料（快速）
```bash
POST /api/v1/query/stock
{"symbol": "AAPL", "include_info": true, "include_prices": true}
```

### 獲取新資料（較慢）
```bash
POST /api/v1/fetch/yahoo
{"symbol": "AAPL", "fetch_info": true, "fetch_historical": true}
```

### 獲取最新價格
```bash
GET /api/v1/stocks/AAPL/prices/latest
```

### 互動式文檔
```
http://127.0.0.1:8001/docs
```

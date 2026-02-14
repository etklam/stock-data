# 配置系統使用指南

## 概述

該項目現在支持雙層配置系統：
1. **config.yaml** - 默認配置（可提交到版本控制）
2. **.env** - 環境變數覆蓋（不提交，用於敏感信息）

## 配置優先級

**環境變數 (.env) > config.yaml**

這意味著：
- `config.yaml` 提供所有配置項的默認值
- `.env` 中的環境變數會覆蓋對應的配置項
- 系統會自動讀取兩個文件並合併配置

## 快速開始

### 1. 基本設置

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 文件，設置你的敏感信息
nano .env  # 或使用你喜歡的編輯器
```

### 2. 必須配置的環境變數

在 `.env` 文件中，至少需要配置：

```bash
# 數據庫連接（必須）
DATABASE_HOST=localhost          # 或你的數據庫服務器地址
DATABASE_PORT=5432
DATABASE_NAME=stocks_data
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password  # 請使用強密碼
```

### 3. 可選配置

其他配置可以根據需要設置：

```bash
# API 服務器（可選，不設置則使用 config.yaml 中的值）
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_WORKERS=1

# Yahoo Finance（可選）
# YAHOO_FETCH_INTERVAL=300
# YAHOO_START_DATE=2020-01-01

# 調度器（可選）
# SCHEDULER_ENABLED=true
# DAILY_FETCH_TIME=18:00
# MAX_RETRIES=3
# RETRY_INTERVAL=60

# 日誌（可選）
# LOG_LEVEL=INFO
# LOG_FILE=logs/stocks_data.log
```

## 配置文件說明

### config.yaml

**用途**: 存儲所有配置項的默認值
**特點**:
- 包含完整的配置結構
- 可以提交到版本控制
- 敏感信息使用占位符或默認值
- 可在 `.env` 中覆蓋任何值

**示例**:
```yaml
database:
  host: localhost       # 可被 DATABASE_HOST 覆蓋
  port: 5432          # 可被 DATABASE_PORT 覆蓋
  name: stocks_data    # 可被 DATABASE_NAME 覆蓋
  user: postgres       # 可被 DATABASE_USER 覆蓋
  password: CHANGE_ME  # 可被 DATABASE_PASSWORD 覆蓋 ⚠️ 必須覆蓋
```

### .env

**用途**: 存儲敏感信息和環境特定的配置
**特點**:
- 在 `.gitignore` 中，不會被提交
- 僅包含需要覆蓋的變數
- 每個環境（開發、測試、生產）可以有不同的 `.env`

**示例**:
```bash
# 必須配置
DATABASE_PASSWORD=my_secure_password

# 可選覆蓋
API_PORT=8080
LOG_LEVEL=DEBUG
```

## 環境變數映射

所有支持環境變數覆蓋的配置項：

| 環境變數 | 配置路徑 | 說明 |
|---------|---------|------|
| `DATABASE_HOST` | `database.host` | 數據庫主機 |
| `DATABASE_PORT` | `database.port` | 數據庫端口 |
| `DATABASE_NAME` | `database.name` | 數據庫名稱 |
| `DATABASE_USER` | `database.user` | 數據庫用戶 |
| `DATABASE_PASSWORD` | `database.password` | 數據庫密碼 ⚠️ |
| `API_HOST` | `api.host` | API 服務器主機 |
| `API_PORT` | `api.port` | API 服務器端口 |
| `API_RELOAD` | `api.reload` | API 自動重載 |
| `API_WORKERS` | `api.workers` | API 工作進程數 |
| `YAHOO_FETCH_INTERVAL` | `yahoo_finance.fetch_interval` | Yahoo Finance 請求間隔 |
| `YAHOO_START_DATE` | `yahoo_finance.start_date` | 歷史數據起始日期 |
| `SCHEDULER_ENABLED` | `scheduler.enabled` | 是否啟用調度器 |
| `DAILY_FETCH_TIME` | `scheduler.daily_fetch_time` | 每日數據獲取時間 |
| `MAX_RETRIES` | `scheduler.max_retries` | 最大重試次數 |
| `RETRY_INTERVAL` | `scheduler.retry_interval` | 重試間隔 |
| `LOG_LEVEL` | `logging.level` | 日誌級別 |
| `LOG_FILE` | `logging.file` | 日誌文件路徑 |
| `LOG_MAX_SIZE` | `logging.max_size` | 日誌文件最大大小 |
| `LOG_BACKUP_COUNT` | `logging.backup_count` | 日誌備份數量 |
| `APP_DEBUG` | `app.debug` | 應用調試模式 |
| `APP_NAME` | `app.name` | 應用名稱 |
| `APP_VERSION` | `app.version` | 應用版本 |

## 數據類型轉換

系統會自動將環境變數字符串轉換為正確的類型：

- **布爾值**: `true`, `yes`, `1` → `True` | `false`, `no`, `0` → `False`
- **整數**: `5432` → `5432`
- **浮點數**: `3.14` → `3.14`
- **字符串**: `localhost` → `"localhost"`

## 安全最佳實踐

### 開發環境
```bash
# .env (開發)
DATABASE_HOST=localhost
DATABASE_PASSWORD=dev_password_123
LOG_LEVEL=DEBUG
APP_DEBUG=true
```

### 生產環境
```bash
# .env.production (生產)
DATABASE_HOST=prod-db-server.example.com
DATABASE_PASSWORD=very_secure_random_password
LOG_LEVEL=WARNING
APP_DEBUG=false
```

### 注意事項
1. ✅ 永遠不要將 `.env` 提交到版本控制
2. ✅ `.env` 已在 `.gitignore` 中
3. ✅ 在 `.env.example` 中提供配置範例
4. ✅ 使用強密碼作為 `DATABASE_PASSWORD`
5. ✅ 生產環境設置 `APP_DEBUG=false`
6. ✅ 生產環境使用 `LOG_LEVEL=WARNING` 或 `ERROR`

## 測試配置

運行配置測試腳本驗證設置：

```bash
python test_config.py
```

輸出應該顯示：
- 數據庫配置（密碼顯示為 ***）
- API 配置
- 調度器配置
- 加載的股票數量
- 環境變數設置狀態

## 故障排除

### 問題: 數據庫連接失敗
**解決方案**:
1. 檢查 `.env` 文件是否存在
2. 驗證 `DATABASE_PASSWORD` 已正確設置
3. 確保數據庫服務器正在運行
4. 測試配置: `python test_config.py`

### 問題: 環境變數沒有生效
**解決方案**:
1. 確保環境變數名稱正確（區分大小寫）
2. 檢查 `.env` 文件格式（沒有空格，使用 `=` 分隔）
3. 重新啟動應用程序

### 問題: 類型錯誤
**解決方案**:
- 布爾值使用: `true` 或 `false`（小寫）
- 數字不要加引號
- 字符串可以加引號也可以不加

## 遷移舊配置

如果你之前直接在 `config.yaml` 中設置所有配置：

1. **備份現有配置**
   ```bash
   cp config.yaml config.yaml.backup
   ```

2. **創建 .env 文件**
   ```bash
   cp .env.example .env
   ```

3. **將敏感信息移到 .env**
   - 將 `database.password` 移到 `DATABASE_PASSWORD`
   - 將其他敏感信息也移動

4. **更新 config.yaml**
   - 使用占位符替換敏感信息
   - 保留非敏感默認值

5. **測試**
   ```bash
   python test_config.py
   ```

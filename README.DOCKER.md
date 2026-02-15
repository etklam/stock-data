# Docker 部署指南

本指南說明如何使用 Docker 和 Docker Compose 部署股票資料系統。

## 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+

## 快速開始

### 1. 準備環境變數文件

```bash
# 複製環境變數範例
cp .env.docker.example .env

# 編輯 .env 文件，修改必要的配置（特別是密碼）
vim .env
```

### 2. 啟動所有服務

```bash
# 啟動 PostgreSQL 和 API 服務
docker-compose up -d

# 查看日誌
docker-compose logs -f api
```

### 3. 初始化資料庫

```bash
# 進入 API 容器
docker-compose exec api bash

# 初始化資料庫表
python main.py --init

# 退出容器
exit
```

### 4. 驗證部署

```bash
# 檢查服務狀態
docker-compose ps

# 檢查 API 健康狀態
curl http://localhost:8000/health

# 訪問 API 文檔
# 在瀏覽器打開：http://localhost:8000/docs
```

## Docker Compose 命令

### 基本操作

```bash
# 啟動所有服務（後台執行）
docker-compose up -d

# 啟動並查看日誌
docker-compose up

# 停止所有服務
docker-compose down

# 停止並刪除所有服務、卷、網絡
docker-compose down -v

# 重啟服務
docker-compose restart

# 查看服務狀態
docker-compose ps

# 查看服務日誌
docker-compose logs -f [service_name]

# 查看特定服務的日誌
docker-compose logs -f api
docker-compose logs -f postgres
```

### 管理命令

```bash
# 進入 API 容器
docker-compose exec api bash

# 進入 PostgreSQL 容器
docker-compose exec postgres bash

# 連接到 PostgreSQL
docker-compose exec postgres psql -U postgres -d stocks_data

# 執行 Python 腳本
docker-compose exec api python main.py --help

# 獲取歷史資料
docker-compose exec api python main.py --historical

# 獲取每日資料
docker-compose exec api python main.py --daily
```

### 更新和重建

```bash
# 重建映像（不使用緩存）
docker-compose build --no-cache

# 重建並啟動
docker-compose up -d --build

# 只重建特定服務
docker-compose build api
docker-compose up -d api
```

## 服務說明

### PostgreSQL 資料庫

- **端口**: 5432（可透過 .env 配置）
- **預設資料庫**: stocks_data
- **預設用戶**: postgres
- **密碼**: 在 .env 中配置
- **資料持久化**: 使用 Docker volume `postgres_data`

### API 服務

- **端口**: 8000（可透過 .env 配置）
- **健康檢查**: 每 30 秒檢查一次
- **日誌**: 掛載到本地 `./logs` 目錄
- **自動重啟**: 除非手動停止

### Adminer（可選）

Adminer 是一個輕量級的資料庫管理工具。

```bash
# 啟動 Adminer
docker-compose --profile admin up -d

# 訪問 Adminer
# 瀏覽器：http://localhost:8080
# 連接信息：
#   - 伺服器：postgres
#   - 用戶：postgres
#   - 密碼：（.env 中的 POSTGRES_PASSWORD）
#   - 資料庫：stocks_data
```

## 環境變數

主要環境變數說明（在 .env 文件中配置）：

| 變數名稱 | 預設值 | 描述 |
|----------|--------|------|
| POSTGRES_PASSWORD | postgres123 | PostgreSQL 密碼 |
| POSTGRES_PORT | 5432 | PostgreSQL 對外端口 |
| API_PORT | 8000 | API 服務對外端口 |
| API_RELOAD | false | API 自動重載（開發模式） |
| API_WORKERS | 4 | API 工作進程數 |
| SCHEDULER_ENABLED | true | 排程器開關 |
| SCHEDULER_DAILY_FETCH_TIME | 18:00 | 每日獲取時間 |
| LOG_LEVEL | INFO | 日誌級別 |
| YAHOO_FETCH_INTERVAL | 300 | Yahoo 獲取間隔（秒） |

## 故障排除

### 啟動失敗

```bash
# 查看詳細日誌
docker-compose logs api

# 檢查資料庫連接
docker-compose exec api python -c "from src.database.connection import db_manager; print(db_manager.test_connection())"
```

### 資料庫連接問題

```bash
# 檢查 PostgreSQL 是否啟動
docker-compose ps postgres

# 檢查 PostgreSQL 日誌
docker-compose logs postgres

# 測試連接
docker-compose exec postgres psql -U postgres -d stocks_data -c "SELECT version();"
```

### 重啟服務

```bash
# 重啟所有服務
docker-compose restart

# 重啟特定服務
docker-compose restart api
docker-compose restart postgres
```

### 清理並重新開始

```bash
# 停止並刪除所有容器、卷、網絡
docker-compose down -v

# 刪除映像
docker-compose down -v --rmi all

# 重新構建並啟動
docker-compose up -d --build
```

## 生產環境建議

### 1. 使用更安全的密碼

```bash
# 在 .env 中使用強密碼
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### 2. 配置反向代理

使用 Nginx 或 Traefik 作為反向代理：

```yaml
# docker-compose.prod.yml 添加 Nginx 服務
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
  depends_on:
    - api
```

### 3. 資料庫備份

```bash
# 備份資料庫
docker-compose exec postgres pg_dump -U postgres stocks_data > backup_$(date +%Y%m%d).sql

# 還原資料庫
docker-compose exec -T postgres psql -U postgres stocks_data < backup_20250215.sql
```

### 4. 日誌管理

```bash
# 定期清理日誌
find ./logs -name "*.log" -mtime +7 -delete

# 或使用 logrotate
```

### 5. 資源限制

在 docker-compose.yml 中添加：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 監控和日誌

### 查看實時日誌

```bash
# 所有服務
docker-compose logs -f

# 特定服務
docker-compose logs -f api
docker-compose logs -f postgres
```

### 查看容器統計

```bash
# 資源使用情況
docker stats stocks-data-api stocks-data-postgres

# 容器詳情
docker inspect stocks-data-api
```

## 更新應用

```bash
# 1. 拉取最新代碼
git pull

# 2. 重建並重啟
docker-compose up -d --build

# 3. 查看重啟日誌
docker-compose logs -f api
```

## 多環境部署

### 開發環境

```bash
# 使用 docker-compose.dev.yml
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 生產環境

```bash
# 使用 docker-compose.prod.yml
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 參考資源

- [Docker 文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)

# 自動化測試指南

## 概述

本項目使用 **pytest** 框架進行自動化測試，包括：
- 單元測試 (Unit Tests)
- 集成測試 (Integration Tests)
- API 測試
- 覆蓋率報告

## 測試結構

```
tests/
├── conftest.py              # pytest 配置和共享 fixtures
├── unit/                   # 單元測試
│   ├── test_config_manager.py
│   ├── test_database_services.py
│   └── test_yahoo_client.py
└── integration/             # 集成測試
    └── test_api.py
```

## 快速開始

### 安裝測試依賴

```bash
# 激活虛擬環境
source venv/bin/activate

# 安裝測試依賴
pip install -r requirements-test.txt
```

### 運行測試

#### 方式 1: 使用便利腳本（推薦）

```bash
./run_tests.sh
```

提供的選項：
1. 運行所有測試
2. 僅運行單元測試
3. 僅運行集成測試
4. 運行特定測試文件
5. 運行特定測試函數
6. 查看測試覆蓋率
7. 快速測試（跳過慢速測試）

#### 方式 2: 直接使用 pytest

```bash
# 運行所有測試
pytest

# 運行單元測試
pytest -m unit

# 運行集成測試
pytest -m integration

# 運行特定文件
pytest tests/unit/test_config_manager.py

# 運行特定測試函數
pytest tests/unit/test_config_manager.py::TestConfigManager::test_load_config_success

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 停在第一個失敗
pytest -x

# 運行上次失敗的測試
pytest --lf
```

## 測試覆蓋率

### 生成覆蓋率報告

```bash
# HTML 報告（推薦）
pytest --cov=src --cov-report=html

# 終端報告
pytest --cov=src --cov-report=term-missing

# 兩者都生成
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### 查看覆蓋率報告

```bash
# 在瀏覽器中打開 HTML 報告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 覆蓋率目標

- **整體目標**: > 80%
- **關鍵模塊**: > 90%
  - config_manager.py
  - database/services.py
  - data_fetcher/yahoo_client.py

## 編寫測試

### 測試命名規範

```python
# 文件命名: test_<module>.py
test_config_manager.py
test_database_services.py

# 類命名: Test<ClassName>
class TestConfigManager:
    pass

# 函數命名: test_<what>_<expected>
def test_load_config_success(self):
    pass

def test_load_config_file_not_found(self):
    pass
```

### 使用 Fixtures

```python
import pytest

from tests.conftest import test_config  # 導入共享 fixture

def test_something(test_config):  # 使用 fixture
    assert test_config['database']['host'] == 'localhost'
```

### 單元測試示例

```python
class TestStockService:
    """股票服務測試"""

    def test_create_stock(self, in_memory_db):
        """測試創建新股票"""
        stock = StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc.'
        )

        assert stock.symbol == 'AAPL'
        assert stock.name == 'Apple Inc.'

    def test_create_stock_duplicate(self, in_memory_db):
        """測試創建重複股票"""
        # 第一次創建
        StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc.'
        )
        in_memory_db.commit()

        # 第二次創建（應更新）
        stock = StockService.create_or_update_stock(
            in_memory_db,
            symbol='AAPL',
            name='Apple Inc. Updated'
        )

        assert stock.name == 'Apple Inc. Updated'
```

### 集成測試示例

```python
class TestAPIEndpoints:
    """API 端點集成測試"""

    def test_get_all_stocks(self, client):
        """測試獲取所有股票"""
        response = client.get("/api/v1/stocks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

### 使用 Mock

```python
from unittest.mock import patch, Mock

def test_external_api_call(self):
    """測試外部 API 調用"""
    mock_response = Mock()
    mock_response.json.return_value = {'data': 'test'}

    with patch('requests.get', return_value=mock_response):
        result = my_function()

    assert result == {'data': 'test'}
```

## 測試標記 (Markers)

使用 `@pytest.mark` 標記測試：

```python
import pytest

@pytest.mark.unit
def test_config_loading():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_large_data_import():
    pass

@pytest.mark.database
def test_database_query():
    pass
```

運行特定標記的測試：

```bash
pytest -m unit        # 只運行單元測試
pytest -m integration # 只運行集成測試
pytest -m "not slow" # 跳過慢速測試
```

## 常見測試場景

### 1. 測試配置管理

```python
def test_env_override():
    """測試環境變數覆蓋配置"""
    # 設置環境變數
    os.environ['DATABASE_HOST'] = 'test-host'

    # 重新加載配置
    manager = ConfigManager()

    # 驗證
    assert manager.get('database.host') == 'test-host'
```

### 2. 測試數據庫操作

```python
def test_database_transaction(in_memory_db):
    """測試數據庫事務"""
    # 創建
    stock = StockService.create_or_update_stock(
        in_memory_db,
        symbol='TEST'
    )
    in_memory_db.commit()

    # 查詢
    found = StockService.get_stock_by_symbol(in_memory_db, 'TEST')
    assert found is not None

    # 刪除
    in_memory_db.delete(stock)
    in_memory_db.commit()

    # 驗證刪除
    found = StockService.get_stock_by_symbol(in_memory_db, 'TEST')
    assert found is None
```

### 3. 測試 API 端點

```python
def test_api_endpoint(client):
    """測試 API 端點"""
    response = client.get("/api/v1/stocks")

    assert response.status_code == 200
    data = response.json()
    assert 'stocks' in data
```

### 4. 測試異常處理

```python
def test_file_not_found():
    """測試文件不存在異常"""
    with pytest.raises(FileNotFoundError):
        ConfigManager("nonexistent.yaml")

def test_invalid_input():
    """測試無效輸入"""
    with pytest.raises(ValueError):
        validate_symbol("")
```

## 調試測試

### 使用 pdb 調試

```bash
# 在失敗時進入調試器
pytest --pdb

# 在測試開始時進入調試器
pytest --trace
```

### 查看輸出

```bash
# 顯示 print 輸出
pytest -s

# 只顯示失敗測試的輸出
pytest -s --tb=short
```

### 詳細錯誤信息

```bash
# 完整回溯
pytest --tb=long

# 簡短回溯
pytest --tb=short

# 只顯示錯誤語句
pytest --tb=line
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run tests
      run: pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 最佳實踐

### ✅ DO

1. **獨立性**: 每個測試應該獨立運行
2. **可重複**: 測試應該可重複執行，結果一致
3. **快速**: 單元測試應該快速（< 1 秒）
4. **清晰**: 測試名稱和描述應該清楚說明測試內容
5. **覆蓋**: 測試應該覆蓋正常和異常情況

### ❌ DON'T

1. 不要在測試中使用真實的數據庫連接
2. 不要依賴測試運行順序
3. 不要在測試之間共享狀態
4. 不要寫過長的測試（拆分為多個測試）
5. 不要過度使用 mock（只在需要時使用）

## 測試檢查清單

在提交代碼前，確保：

- [ ] 所有測試通過
- [ ] 代碼覆蓋率 > 80%
- [ ] 新功能有對應的測試
- [ ] Bug 修復有回歸測試
- [ ] 測試名稱清晰描述測試內容
- [ ] 無過期的測試

## 故障排除

### 問題: 導入錯誤

```
ImportError: No module named 'src'
```

**解決方案**: 確保 `tests/conftest.py` 包含路徑設置：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
```

### 問題: Fixture 未找到

```
fixture 'in_memory_db' not found
```

**解決方案**: 確保 fixture 在 `conftest.py` 中定義或在測試文件中導入。

### 問題: 測試超時

**解決方案**:
- 增加 pytest.ini 中的 timeout 設置
- 或使用 `@pytest.mark.timeout(60)` 標記特定測試

## 相關文件

- `pytest.ini` - pytest 配置
- `conftest.py` - 共享 fixtures
- `run_tests.sh` - 測試運行腳本
- `requirements-test.txt` - 測試依賴

## 參考資料

- [pytest 官方文檔](https://docs.pytest.org/)
- [pytest-cov 覆蓋率](https://pytest-cov.readthedocs.io/)
- [FastAPI 測試](https://fastapi.tiangolo.com/tutorial/testing/)

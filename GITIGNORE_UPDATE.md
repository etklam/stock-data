# .gitignore 更新說明

## 更新日期
2026-02-15

## 概述

重新組織和完善了 `.gitignore` 文件，確保：
- ✅ 敏感信息不會被提交
- ✅ 常見的臨時文件被忽略
- ✅ 清晰的分類和註釋
- ✅ 支持多平台（macOS, Windows, Linux）

## 主要改進

### 1. 結構優化
- ✅ 按類別分組（Python, IDE, 數據庫, 測試等）
- ✅ 清晰的區塊分隔符
- ✅ 每個類別都有說明註釋

### 2. 新增規則

#### 安全性
```gitignore
# 憑證文件
*.pem, *.key, *.crt, *.p12, *.pfx
secrets/、credentials/、.auth/

# 多環境配置
.env.production
.env.development
.env.test
```

#### 項目特定
```gitignore
# 備份和臨時文件
*.bak, *.tmp, *.old, *.orig
temp/, tmp/
```

#### 操作系統特定
```gitignore
# macOS
.DS_Store, ._*

# Windows
Thumbs.db, Desktop.ini

# Linux
.directory, .Trash-*
```

### 3. 修復的問題

| 問題 | 修復 |
|------|------|
| 拼寫錯誤 `__pycache__/` | ✅ 改為 `__pycache__/` |
| 重複的規則 | ✅ 移除重複項 |
| 混亂的順序 | ✅ 邏輯分組 |
| 缺少安全規則 | ✅ 添加憑證/密鑰忽略 |

## 完整的忽略類別

### 🐍 Python 開發
- `__pycache__/` - 編譯的 Python 字節碼
- `*.pyc`, `*.pyo`, `*.pyd` - 編譯文件
- `*.so` - C 擴展
- `build/`, `dist/` - 構建目錄
- `*.egg-info/`, `*.egg` - 打包文件

### 🐳 虛擬環境
- `venv/`, `env/`, `.venv/` - 虛擬環境目錄
- `ENV/` - Pipenv 環境

### 💻 IDE 編輯器
- `.vscode/` - VS Code 設置
- `.idea/` - JetBrains IDE (PyCharm, etc.)
- `*.swp`, `*.swo` - Vim 臨時文件
- `.DS_Store` - macOS 系統文件
- `*.sublime-*` - Sublime Text 設置

### 🔒 安全和敏感信息
- `.env` - 環境變數（重要！）
- `.env.*` - 環境特定配置
- `*.pem`, `*.key` - SSL/TLS 憑證
- `secrets/`, `credentials/` - 敏感目錄

### 📝 日誌和數據
- `logs/`, `*.log` - 應用日誌
- `*.db`, `*.sqlite*` - 數據庫文件
- `*.sql`, `*.dump` - 數據庫備份
- `data/` - 數據目錄

### 🧪 測試和覆蓋率
- `.pytest_cache/` - pytest 緩存
- `.coverage`, `htmlcov/` - 覆蓋率報告
- `.tox/`, `.nox/` - 測試環境

### 📊 Jupyter Notebook
- `.ipynb_checkpoints/` - 自動保存
- `*.ipynb` - Notebook 文件（可選）

### 🎯 項目特定
- `*.bak`, `*.tmp` - 備份和臨時
- `temp/`, `tmp/` - 臨時目錄

### 🔧 類型檢查和工具
- `.mypy_cache/` - mypy 緩存
- `.pyre/`, `.pytype/` - 類型檢查器

### 📦 包管理器
- `Pipfile.lock` - Pipenv 鎖文件
- `poetry.lock` - Poetry 鎖文件

## 使用方法

### 初始化 Git 仓库

提供了便利腳本 `init_git.sh`：

```bash
# 執行初始化腳本
./init_git.sh

# 或手動初始化
git init
git add .
git commit -m "Initial commit"
```

### 驗證 .gitignore

檢查哪些文件會被忽略：

```bash
# 查看被忽略的文件
git check-ignore -v *

# 查看特定文件是否被忽略
git check-ignore -v .env
git check-ignore -v venv/
```

### 添加已被忽略的文件

如果需要添加一個被 .gitignore 匹配的文件：

```bash
# 使用 -f 強制添加
git add -f myfile.log

# 或者暫時忽略規則
git add -f myfile.log
```

### 調試 .gitignore

如果文件沒有被正確忽略：

```bash
# 檢查文件是否已被追蹤
git ls-files | grep myfile

# 如果已被追蹤，先移除
git rm --cached myfile

# 然後它就會被 .gitignore 忽略
```

## 最佳實踐

### ✅ 應該忽略
1. **敏感信息**: `.env`, 憑證, 密鑰
2. **生成的文件**: `__pycache__`, `*.pyc`, 構建產物
3. **虛擬環境**: `venv/`, `env/`
4. **日誌和數據**: `logs/`, `*.db`
5. **IDE 配置**: `.vscode/`, `.idea/`
6. **臨時文件**: `*.tmp`, `*.bak`

### ❌ 不應該忽略
1. **配置文件**: `config.yaml`（不含敏感信息）
2. **源代碼**: `*.py`, `src/`
3. **文檔**: `README.md`, `CONFIG_GUIDE.md`
4. **依賴**: `requirements.txt`
5. **範例文件**: `.env.example`

## 項目特定的考量

對於 Stock Data System 項目：

### 必須提交
- ✅ `config.yaml` - 配置結構和默認值
- ✅ `.env.example` - 環境變數範本
- ✅ 所有源代碼
- ✅ 文檔和腳本

### 必須忽略
- ❌ `.env` - 數據庫密碼等敏感信息
- ❌ `logs/` - 日誌文件
- ❌ `*.db`, `*.sqlite` - 本地數據庫
- ❌ `venv/` - 虛擬環境

### 數據庫文件
如果項目使用 PostgreSQL（如本項目），不需要忽略 `.db` 文件，
因為數據在遠程服務器上。但為了安全起見仍然包含此規則。

### 備份策略
建議定期備份，但不要提交到 git：
```bash
# 創建備份（在 .gitignore 中）
pg_dump stocks_data > backup_$(date +%Y%m%d).sql
```

## 常見問題

### Q: .gitignore 不生效？
**A**: 如果文件已經被 git 追蹤，需要先移除：
```bash
git rm --cached -r .
git add .
```

### Q: 如何忽略所有 .log 文件但保留 special.log？
**A**: 使用否定規則：
```gitignore
*.log
!important.log
```

### Q: 如何忽略目錄但保留其中的某些文件？
**A**:
```gitignore
data/*
!data/.gitkeep
```

### Q: 如何查看實際提交的內容？
**A**: 檢查 git 歷史：
```bash
git log --name-status
git ls-tree -r HEAD
```

## 相關文件

- `init_git.sh` - Git 初始化腳本
- `.gitignore` - Git 忽略規則
- `CONFIG_GUIDE.md` - 配置指南

## 參考資料

- [Git GitHub - .gitignore](https://github.com/github/gitignore)
- [Python .gitignore 模板](https://github.com/github/gitignore/blob/main/Python.gitignore)

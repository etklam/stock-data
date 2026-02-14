"""
配置管理器測試
"""

import os
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from src.config.config_manager import ConfigManager

# 在測試開始時保存原始環境變數
@pytest.fixture(autouse=True)
def isolate_environment():
    """隔離環境變數"""
    original_env = os.environ.copy()
    yield
    # 測試後恢復原始環境
    os.environ.clear()
    os.environ.update(original_env)


class TestConfigManager:
    """配置管理器測試類"""

    def test_load_config_success(self, tmp_path, test_config):
        """測試成功加載配置文件"""
        # 創建測試配置文件
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        # 加載配置
        manager = ConfigManager(str(config_file))

        # 驗證
        assert manager.get('database.host') == 'localhost'
        assert manager.get('database.port') == 5432
        assert manager.get('database.name') == 'stocks_data_test'

    def test_load_config_file_not_found(self, tmp_path):
        """測試配置文件不存在"""
        config_file = tmp_path / "nonexistent.yaml"

        # 清除環境變數以避免干擾
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):  # ConfigManager 現在拋出通用 Exception
                ConfigManager(str(config_file))

    def test_get_with_default(self, tmp_path, test_config):
        """測試獲取配置時使用默認值"""
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        manager = ConfigManager(str(config_file))

        # 獲取存在的鍵
        assert manager.get('database.host') == 'localhost'

        # 獲取不存在的鍵，使用默認值
        assert manager.get('nonexistent.key', 'default') == 'default'
        assert manager.get('nonexistent.key') is None

    def test_get_database_config(self, tmp_path, test_config):
        """測試獲取數據庫配置"""
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        manager = ConfigManager(str(config_file))
        db_config = manager.get_database_config()

        assert db_config['host'] == 'localhost'
        assert db_config['port'] == 5432
        assert db_config['name'] == 'stocks_data_test'
        assert db_config['user'] == 'test_user'
        assert db_config['password'] == 'test_password'

    def test_get_scheduler_config(self, tmp_path):
        """測試獲取調度器配置"""
        config_data = {
            'scheduler': {
                'enabled': True,
                'daily_fetch_time': '18:00',
                'max_retries': 3
            }
        }
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)

        manager = ConfigManager(str(config_file))
        scheduler_config = manager.get_scheduler_config()

        assert scheduler_config['enabled'] is True
        assert scheduler_config['daily_fetch_time'] == '18:00'
        assert scheduler_config['max_retries'] == 3

    @patch.dict(os.environ, {'DATABASE_HOST': 'test-host', 'DATABASE_PORT': '9999'}, clear=True)
    def test_env_override(self, tmp_path, test_config):
        """測試環境變數覆蓋配置"""
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        # 清除環境變數並測試
        import os as os_module
        original_env = os_module.environ.copy()
        try:
            os_module.environ.clear()
            os_module.environ['DATABASE_HOST'] = 'test-host'
            os_module.environ['DATABASE_PORT'] = '9999'

            manager = ConfigManager(str(config_file), env_file=tmp_path / ".env")

            # 環境變數應該覆蓋配置文件
            assert manager.get('database.host') == 'test-host'
            assert manager.get('database.port') == 9999
        finally:
            os_module.environ.clear()
            os_module.environ.update(original_env)

    def test_convert_env_value_bool(self):
        """測試環境變數類型轉換 - 布爾值"""
        manager = ConfigManager()

        assert manager._convert_env_value('true') is True
        assert manager._convert_env_value('True') is True
        assert manager._convert_env_value('yes') is True
        assert manager._convert_env_value('1') is True

        assert manager._convert_env_value('false') is False
        assert manager._convert_env_value('False') is False
        assert manager._convert_env_value('no') is False
        assert manager._convert_env_value('0') is False

    def test_convert_env_value_number(self):
        """測試環境變數類型轉換 - 數字"""
        manager = ConfigManager()

        assert manager._convert_env_value('123') == 123
        assert manager._convert_env_value('3.14') == 3.14
        assert isinstance(manager._convert_env_value('123'), int)
        assert isinstance(manager._convert_env_value('3.14'), float)

    def test_convert_env_value_string(self):
        """測試環境變數類型轉換 - 字符串"""
        manager = ConfigManager()

        assert manager._convert_env_value('localhost') == 'localhost'
        assert isinstance(manager._convert_env_value('localhost'), str)

    def test_reload_config(self, tmp_path, test_config):
        """測試重新加載配置"""
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        manager = ConfigManager(str(config_file))
        assert manager.get('database.host') == 'localhost'

        # 修改配置文件
        test_config['database']['host'] = 'modified-host'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        # 重新加載
        manager.reload()
        assert manager.get('database.host') == 'modified-host'

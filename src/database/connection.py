"""
數據庫連接管理
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Optional, Generator
import logging

from ..config.config_manager import config
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """數據庫管理器"""
    
    def __init__(self):
        """初始化數據庫管理器"""
        self._engine = None
        self._session_factory = None
        self._connection_params = self._get_connection_params()
    
    def _get_connection_params(self) -> dict:
        """獲取數據庫連接參數"""
        db_config = config.get_database_config()
        return {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432),
            'database': db_config.get('name', 'stocks_data'),
            'user': db_config.get('user', 'postgres'),
            'password': db_config.get('password', ''),
        }
    
    def get_connection_string(self) -> str:
        """獲取數據庫連接字符串"""
        params = self._connection_params
        return f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
    
    def initialize_engine(self) -> None:
        """初始化 SQLAlchemy 引擎"""
        try:
            connection_string = self.get_connection_string()
            self._engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # 設為 True 可查看 SQL 語句
            )
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info("數據庫引擎初始化成功")
        except Exception as e:
            logger.error(f"數據庫引擎初始化失敗: {e}")
            raise
    
    def create_tables(self) -> None:
        """創建所有表"""
        try:
            if self._engine is None:
                self.initialize_engine()
            
            Base.metadata.create_all(self._engine)
            logger.info("數據庫表創建成功")
        except Exception as e:
            logger.error(f"創建數據庫表失敗: {e}")
            raise
    
    def get_session(self) -> Session:
        """獲取數據庫會話"""
        if self._session_factory is None:
            self.initialize_engine()
        return self._session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """提供事務範圍的會話上下文管理器"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"數據庫事務失敗: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """測試數據庫連接"""
        try:
            with psycopg2.connect(**self._connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"數據庫連接測試失敗: {e}")
            return False
    
    def close(self) -> None:
        """關閉數據庫連接"""
        if self._engine:
            self._engine.dispose()
            logger.info("數據庫連接已關閉")


class RawQueryExecutor:
    """原始 SQL 查詢執行器（僅用於特殊情況）"""
    
    def __init__(self, connection_params: dict):
        """初始化原始查詢執行器"""
        self._connection_params = connection_params
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """執行查詢並返回結果"""
        try:
            with psycopg2.connect(**self._connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    if query.strip().upper().startswith('SELECT'):
                        return cursor.fetchall()
                    else:
                        conn.commit()
                        return [{'affected_rows': cursor.rowcount}]
        except Exception as e:
            logger.error(f"執行原始 SQL 查詢失敗: {e}")
            raise
    
    def execute_script(self, script: str) -> None:
        """執行 SQL 腳本"""
        try:
            with psycopg2.connect(**self._connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(script)
                    conn.commit()
                    logger.info("SQL 腳本執行成功")
        except Exception as e:
            logger.error(f"執行 SQL 腳本失敗: {e}")
            raise


# 全局數據庫管理器實例
db_manager = DatabaseManager()

# 全局原始查詢執行器實例（僅用於特殊情況）
raw_query_executor = RawQueryExecutor(db_manager._connection_params)
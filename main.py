"""
股票數據獲取系統主程序
"""

import sys
import argparse
import signal
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.logger import setup_logging, get_logger
from src.config.config_manager import config
from src.database.connection import db_manager
from src.data_fetcher.data_service import DataFetchService
from src.scheduler.task_scheduler import task_scheduler

logger = get_logger(__name__)


class StockDataSystem:
    """股票數據系統主類"""
    
    def __init__(self):
        """初始化系統"""
        self.running = False
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信號處理器"""
        logger.info(f"收到信號 {signum}，正在關閉系統...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """初始化系統"""
        try:
            logger.info("正在初始化股票數據系統...")
            
            # 初始化日誌系統
            setup_logging()
            
            # 測試數據庫連接
            if not db_manager.test_connection():
                raise Exception("數據庫連接失敗")
            
            # 初始化數據庫引擎
            db_manager.initialize_engine()
            
            # 創建數據庫表
            db_manager.create_tables()
            
            logger.info("系統初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"系統初始化失敗: {e}")
            return False
    
    def start_scheduler(self):
        """啟動調度器"""
        try:
            task_scheduler.start()
            logger.info("調度器已啟動")
        except Exception as e:
            logger.error(f"啟動調度器失敗: {e}")
            raise
    
    def fetch_historical_data(self, symbols=None):
        """獲取歷史數據"""
        try:
            data_service = DataFetchService()
            
            if symbols:
                # 獲取指定股票的歷史數據
                for symbol in symbols:
                    logger.info(f"正在獲取 {symbol} 的歷史數據...")
                    success, count = data_service.fetch_and_store_historical_data(symbol)
                    if success:
                        logger.info(f"{symbol} 歷史數據獲取成功，記錄數: {count}")
                    else:
                        logger.error(f"{symbol} 歷史數據獲取失敗")
            else:
                # 獲取所有股票的歷史數據
                logger.info("正在獲取所有股票的歷史數據...")
                results = data_service.fetch_all_stocks_historical()
                
                success_count = sum(1 for success, _ in results.values() if success)
                total_count = len(results)
                
                logger.info(f"歷史數據獲取完成: 成功 {success_count}/{total_count}")
                
                # 顯示詳細結果
                for symbol, (success, count) in results.items():
                    status = "成功" if success else "失敗"
                    logger.info(f"{symbol}: {status}, 記錄數: {count}")
            
        except Exception as e:
            logger.error(f"獲取歷史數據失敗: {e}")
            raise
    
    def fetch_daily_data(self, symbols=None):
        """獲取每日數據"""
        try:
            data_service = DataFetchService()
            
            if symbols:
                # 獲取指定股票的每日數據
                for symbol in symbols:
                    logger.info(f"正在獲取 {symbol} 的每日數據...")
                    success = data_service.fetch_and_store_daily_data(symbol)
                    if success:
                        logger.info(f"{symbol} 每日數據獲取成功")
                    else:
                        logger.error(f"{symbol} 每日數據獲取失敗")
            else:
                # 獲取所有股票的每日數據
                logger.info("正在獲取所有股票的每日數據...")
                results = data_service.fetch_all_stocks_daily()
                
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                logger.info(f"每日數據獲取完成: 成功 {success_count}/{total_count}")
                
                # 顯示詳細結果
                for symbol, success in results.items():
                    status = "成功" if success else "失敗"
                    logger.info(f"{symbol}: {status}")
            
        except Exception as e:
            logger.error(f"獲取每日數據失敗: {e}")
            raise
    
    def update_stock_info(self, symbols=None):
        """更新股票信息"""
        try:
            data_service = DataFetchService()
            
            if symbols:
                # 更新指定股票的信息
                for symbol in symbols:
                    logger.info(f"正在更新 {symbol} 的信息...")
                    success = data_service.fetch_and_store_stock_info(symbol)
                    if success:
                        logger.info(f"{symbol} 信息更新成功")
                    else:
                        logger.error(f"{symbol} 信息更新失敗")
            else:
                # 更新所有股票的信息
                logger.info("正在更新所有股票的信息...")
                results = data_service.update_stock_info_for_all()
                
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                logger.info(f"股票信息更新完成: 成功 {success_count}/{total_count}")
                
                # 顯示詳細結果
                for symbol, success in results.items():
                    status = "成功" if success else "失敗"
                    logger.info(f"{symbol}: {status}")
            
        except Exception as e:
            logger.error(f"更新股票信息失敗: {e}")
            raise
    
    def run_daemon(self):
        """以守護進程模式運行"""
        try:
            logger.info("啟動守護進程模式...")
            self.running = True
            
            # 啟動調度器
            self.start_scheduler()
            
            # 保持程序運行
            while self.running:
                try:
                    import time
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
            
        except Exception as e:
            logger.error(f"守護進程運行失敗: {e}")
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """關閉系統"""
        logger.info("正在關閉系統...")
        self.running = False
        
        # 關閉調度器
        try:
            task_scheduler.shutdown()
        except Exception as e:
            logger.error(f"關閉調度器失敗: {e}")
        
        # 關閉數據庫連接
        try:
            db_manager.close()
        except Exception as e:
            logger.error(f"關閉數據庫連接失敗: {e}")
        
        logger.info("系統已關閉")


def start_api_server(host=None, port=None, reload=None, workers=None):
    """啟動 API 服務器"""
    try:
        # 導入 uvicorn 和 api_server
        from uvicorn import run
        from api_server import app
        
        # 獲取配置參數
        api_host = host or config.get('api.host', '0.0.0.0')
        api_port = port or config.get('api.port', 8000)
        api_reload = reload if reload is not None else config.get('api.reload', True)
        api_workers = workers or config.get('api.workers', 1)
        
        # 初始化系統
        system = StockDataSystem()
        if not system.initialize():
            logger.error("系統初始化失敗，退出")
            sys.exit(1)
        
        logger.info(f"啟動 Stock Data API 服務器於 {api_host}:{api_port}")
        logger.info(f"Swagger UI: http://{api_host}:{api_port}/docs")
        logger.info(f"ReDoc: http://{api_host}:{api_port}/redoc")
        
        # 啟動服務器
        # reload 模式需要使用 import string
        app_str = 'api_server:app' if api_reload else app
        run(
            app_str,
            host=api_host,
            port=api_port,
            reload=api_reload,
            workers=api_workers if not api_reload else 1,  # reload 模式下只能用 1 個 worker
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"啟動 API 服務器失敗: {e}")
        sys.exit(1)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='股票數據獲取系統')
    
    # 全局參數
    parser.add_argument('--config', default='config.yaml', help='指定配置文件路徑')
    parser.add_argument('--init', action='store_true', help='初始化系統')
    parser.add_argument('--historical', nargs='*', help='獲取歷史數據，可指定股票代碼')
    parser.add_argument('--daily', nargs='*', help='獲取每日數據，可指定股票代碼')
    parser.add_argument('--update-info', nargs='*', help='更新股票信息，可指定股票代碼')
    parser.add_argument('--daemon', action='store_true', help='以守護進程模式運行')
    
    # 創建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # CLI 命令（默認行為）
    cli_parser = subparsers.add_parser('cli', help='使用 CLI 模式（默認）')
    cli_parser.add_argument('--init', action='store_true', help='初始化系統')
    cli_parser.add_argument('--historical', nargs='*', help='獲取歷史數據，可指定股票代碼')
    cli_parser.add_argument('--daily', nargs='*', help='獲取每日數據，可指定股票代碼')
    cli_parser.add_argument('--update-info', nargs='*', help='更新股票信息，可指定股票代碼')
    cli_parser.add_argument('--daemon', action='store_true', help='以守護進程模式運行')
    
    # API 命令
    api_parser = subparsers.add_parser('api', help='啟動 API 服務器')
    api_parser.add_argument('--host', default=None, help='指定主機地址')
    api_parser.add_argument('--port', type=int, default=None, help='指定端口')
    api_parser.add_argument('--reload', action='store_true', help='啟用重載（開發模式）')
    api_parser.add_argument('--no-reload', action='store_true', help='禁用重載')
    api_parser.add_argument('--workers', type=int, default=None, help='指定工作進程數')
    
    args = parser.parse_args()
    
    # 處理 API 命令
    if args.command == 'api':
        # 處理 reload 參數
        reload = None
        if args.reload:
            reload = True
        elif args.no_reload:
            reload = False
        
        start_api_server(
            host=args.host,
            port=args.port,
            reload=reload,
            workers=args.workers
        )
        return
    
    # 處理 CLI 命令（包括全局參數）
    # 創建系統實例
    system = StockDataSystem()
    
    try:
        # 初始化系統
        if not system.initialize():
            logger.error("系統初始化失敗，退出")
            sys.exit(1)
        
        # 根據參數執行相應操作
        if args.init:
            logger.info("系統初始化完成")
        
        elif args.historical is not None:
            system.fetch_historical_data(args.historical)
        
        elif args.daily is not None:
            system.fetch_daily_data(args.daily)
        
        elif args.update_info is not None:
            system.update_stock_info(args.update_info)
        
        elif args.daemon:
            system.run_daemon()
        
        else:
            # 默認顯示幫助信息
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("用戶中斷操作")
    except Exception as e:
        logger.error(f"程序執行失敗: {e}")
        sys.exit(1)
    finally:
        system.shutdown()


if __name__ == '__main__':
    main()
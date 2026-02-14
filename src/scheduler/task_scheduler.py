"""
任務調度器
使用 APScheduler 實現定時任務
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime, time as time_obj
import logging
import atexit
from typing import Dict, Callable, Any

from ..data_fetcher.data_service import DataFetchService
from ..database.services import DataFetchLogService
from ..database.connection import db_manager
from ..config.config_manager import config

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任務調度器"""
    
    def __init__(self):
        """初始化調度器"""
        self.scheduler = BackgroundScheduler()
        self.data_service = DataFetchService()
        self.scheduler_config = config.get_scheduler_config()
        self.is_running = False
        
        # 添加事件監聽器
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        # 註冊退出處理
        atexit.register(self.shutdown)
    
    def _job_executed(self, event):
        """任務執行完成事件處理"""
        logger.info(f"任務執行完成: {event.job_id}")
    
    def _job_error(self, event):
        """任務執行錯誤事件處理"""
        logger.error(f"任務執行失敗: {event.job_id}, 異常: {event.exception}")
    
    def start(self):
        """啟動調度器"""
        if not self.scheduler_config.get('enabled', True):
            logger.info("調度器已禁用")
            return
        
        try:
            # 添加每日數據獲取任務
            daily_time = self.scheduler_config.get('daily_fetch_time', '18:00')
            hour, minute = map(int, daily_time.split(':'))
            
            self.scheduler.add_job(
                func=self._daily_data_fetch_job,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_data_fetch',
                name='每日股票數據獲取',
                replace_existing=True,
                max_instances=1
            )
            
            # 添加每小時檢查缺失數據任務
            self.scheduler.add_job(
                func=self._check_missing_data_job,
                trigger=IntervalTrigger(hours=1),
                id='check_missing_data',
                name='檢查缺失數據',
                replace_existing=True,
                max_instances=1
            )
            
            # 添加每週更新股票信息任務
            self.scheduler.add_job(
                func=self._update_stock_info_job,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='weekly_update_stock_info',
                name='每週更新股票信息',
                replace_existing=True,
                max_instances=1
            )
            
            # 啟動調度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info("任務調度器啟動成功")
            
        except Exception as e:
            logger.error(f"啟動任務調度器失敗: {e}")
            raise
    
    def shutdown(self):
        """關閉調度器"""
        if self.is_running:
            try:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("任務調度器已關閉")
            except Exception as e:
                logger.error(f"關閉任務調度器失敗: {e}")
    
    def _daily_data_fetch_job(self):
        """每日數據獲取任務"""
        logger.info("開始執行每日數據獲取任務")
        
        try:
            # 獲取所有股票的每日數據
            results = self.data_service.fetch_all_stocks_daily()
            
            # 統計結果
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            logger.info(f"每日數據獲取完成: 成功 {success_count}/{total_count}")
            
            # 記錄任務執行日誌
            with db_manager.session_scope() as session:
                DataFetchLogService.create_log(
                    session,
                    fetch_type='scheduled_daily',
                    status='success' if success_count == total_count else 'partial',
                    records_count=success_count,
                    error_message=f"失敗: {total_count - success_count}" if success_count < total_count else None
                )
                
        except Exception as e:
            logger.error(f"每日數據獲取任務失敗: {e}")
            
            # 記錄錯誤日誌
            try:
                with db_manager.session_scope() as session:
                    DataFetchLogService.create_log(
                        session,
                        fetch_type='scheduled_daily',
                        status='failed',
                        error_message=str(e)
                    )
            except Exception as log_error:
                logger.error(f"記錄錯誤日誌失敗: {log_error}")
    
    def _check_missing_data_job(self):
        """檢查缺失數據任務"""
        logger.info("開始檢查缺失數據")
        
        try:
            symbols = config.get('yahoo_finance.symbols', [])
            missing_count = 0
            
            for symbol in symbols:
                missing_dates = self.data_service.get_missing_data_dates(symbol)
                if missing_dates:
                    logger.warning(f"發現缺失數據: {symbol}, 缺失天數: {len(missing_dates)}")
                    missing_count += len(missing_dates)
                    
                    # 可以在這裡添加自動補充邏輯
                    # 例如：獲取最近7天的缺失數據
                    recent_missing = missing_dates[-7:] if len(missing_dates) > 7 else missing_dates
                    if recent_missing:
                        start_date = recent_missing[0].strftime('%Y-%m-%d')
                        end_date = recent_missing[-1].strftime('%Y-%m-%d')
                        success, count = self.data_service.fetch_and_store_historical_data(
                            symbol, start_date, end_date
                        )
                        if success:
                            logger.info(f"補充缺失數據成功: {symbol}, 補充記錄數: {count}")
            
            logger.info(f"缺失數據檢查完成，總缺失: {missing_count} 條記錄")
            
        except Exception as e:
            logger.error(f"檢查缺失數據失敗: {e}")
    
    def _update_stock_info_job(self):
        """更新股票信息任務"""
        logger.info("開始更新股票信息")
        
        try:
            results = self.data_service.update_stock_info_for_all()
            
            # 統計結果
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            logger.info(f"股票信息更新完成: 成功 {success_count}/{total_count}")
            
        except Exception as e:
            logger.error(f"更新股票信息失敗: {e}")
    
    def add_custom_job(self, job_id: str, func: Callable, trigger, **kwargs):
        """
        添加自定義任務
        
        Args:
            job_id: 任務ID
            func: 任務函數
            trigger: 觸發器
            **kwargs: 其他參數
        """
        try:
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"添加自定義任務成功: {job_id}")
        except Exception as e:
            logger.error(f"添加自定義任務失敗 {job_id}: {e}")
            raise
    
    def remove_job(self, job_id: str):
        """
        移除任務
        
        Args:
            job_id: 任務ID
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"移除任務成功: {job_id}")
        except Exception as e:
            logger.error(f"移除任務失敗 {job_id}: {e}")
            raise
    
    def pause_job(self, job_id: str):
        """
        暫停任務
        
        Args:
            job_id: 任務ID
        """
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"暫停任務成功: {job_id}")
        except Exception as e:
            logger.error(f"暫停任務失敗 {job_id}: {e}")
            raise
    
    def resume_job(self, job_id: str):
        """
        恢復任務
        
        Args:
            job_id: 任務ID
        """
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"恢復任務成功: {job_id}")
        except Exception as e:
            logger.error(f"恢復任務失敗 {job_id}: {e}")
            raise
    
    def get_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        獲取所有任務信息
        
        Returns:
            任務信息字典
        """
        jobs = {}
        for job in self.scheduler.get_jobs():
            jobs[job.id] = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger),
            }
        return jobs
    
    def run_job_now(self, job_id: str):
        """
        立即執行任務
        
        Args:
            job_id: 任務ID
        """
        try:
            self.scheduler.run_job(job_id)
            logger.info(f"立即執行任務: {job_id}")
        except Exception as e:
            logger.error(f"立即執行任務失敗 {job_id}: {e}")
            raise


# 全局調度器實例
task_scheduler = TaskScheduler()
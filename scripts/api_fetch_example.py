#!/usr/bin/env python3
"""
使用API獲取股票資料的範例腳本
"""

import requests
import json
from datetime import datetime, timedelta

def fetch_stock_data(symbol, start_date=None, end_date=None, include_info=True, include_historical=True):
    """
    使用API獲取股票資料
    
    Args:
        symbol: 股票代碼
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        include_info: 是否包含基本信息
        include_historical: 是否包含歷史資料
        
    Returns:
        API響應結果
    """
    url = "http://127.0.0.1:8001/api/v1/fetch/stock"
    
    payload = {
        "symbol": symbol,
        "include_info": include_info,
        "include_historical": include_historical
    }
    
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API請求失敗: {e}")
        return None

def main():
    """主函數 - 演示API使用"""
    
    print("=== 股票資料獲取API使用範例 ===\n")
    
    # 範例1: 獲取TSLA的完整資料（預設過去1年）
    print("1. 獲取TSLA的完整資料（預設過去1年）")
    result = fetch_stock_data("TSLA")
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"基本信息獲取: {result['info_fetched']}")
        print(f"歷史資料獲取: {result['historical_fetched']}")
        print(f"記錄數量: {result['records_count']}")
        if result.get('error'):
            print(f"錯誤信息: {result['error']}")
    print()
    
    # 範例2: 獲取NVDA指定日期範圍的資料
    print("2. 獲取NVDA 2025年的資料")
    result = fetch_stock_data(
        "NVDA", 
        start_date="2025-01-01", 
        end_date="2025-12-31"
    )
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"記錄數量: {result['records_count']}")
    print()
    
    # 範例3: 只獲取AMZN的基本信息
    print("3. 只獲取AMZN的基本信息")
    result = fetch_stock_data("AMZN", include_historical=False)
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"基本信息獲取: {result['info_fetched']}")
        print(f"歷史資料獲取: {result['historical_fetched']}")
    print()
    
    # 範例4: 只獲取META的歷史資料
    print("4. 只獲取META的歷史資料")
    result = fetch_stock_data("META", include_info=False)
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"基本信息獲取: {result['info_fetched']}")
        print(f"歷史資料獲取: {result['historical_fetched']}")
        print(f"記錄數量: {result['records_count']}")
    print()
    
    print("=== API使用說明 ===")
    print("API端點: POST http://127.0.0.1:8001/api/v1/fetch/stock")
    print("請求參數:")
    print("  - symbol (必填): 股票代碼，如 'AAPL', 'MSFT'")
    print("  - start_date (選填): 開始日期，格式 YYYY-MM-DD")
    print("  - end_date (選填): 結束日期，格式 YYYY-MM-DD")
    print("  - include_info (選填): 是否獲取基本信息，預設 true")
    print("  - include_historical (選填): 是否獲取歷史資料，預設 true")
    print()
    print("響應格式:")
    print("  - symbol: 股票代碼")
    print("  - success: 整體成功狀態")
    print("  - info_fetched: 基本信息是否獲取成功")
    print("  - historical_fetched: 歷史資料是否獲取成功")
    print("  - records_count: 獲取的歷史記錄數量")
    print("  - message: 操作訊息")
    print("  - error: 錯誤信息（如果有的話）")

if __name__ == "__main__":
    main()
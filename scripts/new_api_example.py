#!/usr/bin/env python3
"""
新的API結構使用範例 - 分為查詢和獲取兩部分
"""

import requests
import json
from datetime import datetime, timedelta

def query_stock_from_database(symbol, include_info=True, include_prices=True, 
                           start_date=None, end_date=None, limit=100):
    """
    從資料庫查詢股票資料
    
    Args:
        symbol: 股票代碼
        include_info: 是否包含基本信息
        include_prices: 是否包含價格資料
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        limit: 最大記錄數
        
    Returns:
        API響應結果
    """
    url = "http://127.0.0.1:8001/api/v1/query/stock"
    
    payload = {
        "symbol": symbol,
        "include_info": include_info,
        "include_prices": include_prices,
        "limit": limit
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
        print(f"查詢API請求失敗: {e}")
        return None

def fetch_stock_from_yahoo(symbol, fetch_info=True, fetch_historical=True,
                          start_date=None, end_date=None):
    """
    從Yahoo Finance獲取股票資料並儲存到資料庫
    
    Args:
        symbol: 股票代碼
        fetch_info: 是否獲取基本信息
        fetch_historical: 是否獲取歷史資料
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        
    Returns:
        API響應結果
    """
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
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"獲取API請求失敗: {e}")
        return None

def main():
    """主函數 - 演示新的API結構"""
    
    print("=== 新API結構使用範例 ===\n")
    
    # 範例1: 從Yahoo獲取新股票資料
    print("1. 從Yahoo Finance獲取INTC的資料")
    result = fetch_stock_from_yahoo("INTC", fetch_info=True, fetch_historical=True)
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"基本信息獲取: {result['info_fetched']}")
        print(f"歷史資料獲取: {result['historical_fetched']}")
        print(f"記錄數量: {result['records_count']}")
        if result.get('error'):
            print(f"錯誤信息: {result['error']}")
    print()
    
    # 範例2: 從資料庫查詢已存在的股票資料
    print("2. 從資料庫查詢AAPL的資料")
    result = query_stock_from_database("AAPL", include_info=True, include_prices=True, limit=3)
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"找到資料: {result['found']}")
        print(f"價格記錄數: {result['total_price_records']}")
        if result['stock_info']:
            print(f"公司名稱: {result['stock_info']['name']}")
            print(f"交易所: {result['stock_info']['exchange']}")
        if result['prices']:
            print(f"最新價格: {result['prices'][0]['close_price']}")
    print()
    
    # 範例3: 只獲取股票基本信息（不獲取歷史資料）
    print("3. 只從Yahoo獲取AMD的基本信息")
    result = fetch_stock_from_yahoo("AMD", fetch_info=True, fetch_historical=False)
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"基本信息獲取: {result['info_fetched']}")
        print(f"歷史資料獲取: {result['historical_fetched']}")
    print()
    
    # 範例4: 獲取指定日期範圍的歷史資料
    print("4. 獲取NVDA 2025年的歷史資料")
    result = fetch_stock_from_yahoo(
        "NVDA", 
        fetch_info=False, 
        fetch_historical=True,
        start_date="2025-01-01",
        end_date="2025-12-31"
    )
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"成功狀態: {result['success']}")
        print(f"記錄數量: {result['records_count']}")
    print()
    
    # 範例5: 查詢指定日期範圍的價格資料
    print("5. 查詢MSFT最近5天的價格資料")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    result = query_stock_from_database(
        "MSFT", 
        include_info=False, 
        include_prices=True,
        start_date=start_date,
        end_date=end_date
    )
    if result:
        print(f"股票代碼: {result['symbol']}")
        print(f"找到資料: {result['found']}")
        print(f"價格記錄數: {result['total_price_records']}")
        for price in result['prices']:
            print(f"  日期: {price['date'][:10]}, 收盤價: {price['close_price']}")
    print()
    
    print("=== 新API結構說明 ===")
    print()
    print("1. 資料庫查詢API:")
    print("   端點: POST http://127.0.0.1:8001/api/v1/query/stock")
    print("   用途: 從本地資料庫查詢已儲存的股票資料")
    print("   特點: 快速響應，不調用外部API")
    print()
    print("2. Yahoo獲取API:")
    print("   端點: POST http://127.0.0.1:8001/api/v1/fetch/yahoo")
    print("   用途: 從Yahoo Finance獲取新資料並儲存到資料庫")
    print("   特點: 獲取最新資料，處理時間較長")
    print()
    print("3. 工作流程建議:")
    print("   - 先使用查詢API檢查資料是否已存在")
    print("   - 如需最新資料，再使用獲取API從Yahoo更新")
    print("   - 可以根據需求選擇只獲取基本信息或歷史資料")

if __name__ == "__main__":
    main()
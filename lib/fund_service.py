import flet as ft
import akshare as ak
import pandas as pd
import threading
import time
from datetime import datetime
from dataclasses import dataclass

@dataclass
class FundInfo:
    code: str
    name: str
    daily_limit: float
    status: str
    last_update: str

class FundService:
    def __init__(self):
        self.funds_cache = {}
        
    def get_fund_purchase_status(self, fund_codes=None) -> pd.DataFrame:
        try:
            df = ak.fund_purchase_em()
            if fund_codes:
                df = df[df['基金代码'].isin(fund_codes)]
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def get_fund_limit(self, fund_code: str) -> FundInfo:
        try:
            df = ak.fund_purchase_em()
            fund_data = df[df['基金代码'] == fund_code]
            if fund_data.empty:
                return None
            row = fund_data.iloc[0]
            return FundInfo(
                code=str(row['基金代码']),
                name=str(row['基金简称']),
                daily_limit=float(row.get('日累计限定金额', 0)),
                status=str(row.get('申购状态', '未知')),
                last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_all_funds(self) -> pd.DataFrame:
        return self.get_fund_purchase_status()
    
    def search_funds(self, keyword: str) -> pd.DataFrame:
        df = self.get_all_funds()
        if keyword:
            mask = df['基金代码'].astype(str).str.contains(keyword) | \
                   df['基金简称'].str.contains(keyword)
            df = df[mask]
        return df.head(100)
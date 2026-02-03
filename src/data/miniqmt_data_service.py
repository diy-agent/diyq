"""
miniqmt 数据服务模块
封装 miniqmt (xtquant) 的数据获取功能
"""

import sys
import os
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

try:
    import xtquant.xtdata as xtdata
    import xtquant.xtconstant as xtconstant
    from xtquant import XtDataClient
    MINIQMT_AVAILABLE = True
except ImportError:
    logger.warning("xtquant 库未安装，无法使用 miniqmt 数据服务。请从券商获取安装包。")
    MINIQMT_AVAILABLE = False


class MiniQMTDataService:
    """
    miniqmt 数据服务类
    提供与现有 DataDownloader 类兼容的接口，但使用 miniqmt 获取实时数据
    """
    
    def __init__(self, miniqmt_path: Optional[str] = None):
        """
        初始化 miniqmt 数据服务
        
        :param miniqmt_path: miniqmt 安装路径（如果需要手动指定）
        """
        if miniqmt_path:
            sys.path.append(miniqmt_path)
        
        if not MINIQMT_AVAILABLE:
            raise ImportError(
                "xtquant 库未安装。请先从券商获取 miniqmt 安装包并安装。\n"
                "通常需要：\n"
                "1. 联系券商开通 miniqmt 权限\n"
                "2. 下载对应的 xtquant 库\n"
                "3. 将其安装到 site-packages 目录"
            )
        
        logger.info("miniqmt 数据服务初始化成功")
    
    def get_stock_list(self, market: str = "SH",板块: str = None) -> List[Dict]:
        """
        获取股票列表
        
        :param market: 市场代码，'SH' 或 'SZ'
        :param 板块: 板块筛选条件
        :return: 股票列表
        """
        if not MINIQMT_AVAILABLE:
            return []
        
        try:
            # 获取指定市场的股票列表
            stock_list = xtdata.get_stock_list_in_sector(sector=market)
            
            result = []
            for code in stock_list:
                result.append({
                    'code': code,
                    'name': xtdata.get_instrument_detail(code)['InstrumentName'],
                    'market': market
                })
            
            return result
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    def get_etf_list(self) -> List[Dict]:
        """
        获取 ETF 列表
        
        :return: ETF 列表
        """
        if not MINIQMT_AVAILABLE:
            return []
        
        try:
            # 获取 ETF 列表
            etf_list = xtdata.get_stock_list_in_sector(sector='ETF')
            
            result = []
            for code in etf_list:
                result.append({
                    'code': code,
                    'name': xtdata.get_instrument_detail(code)['InstrumentName'],
                    'market': code.split('.')[1] if '.' in code else 'Unknown'
                })
            
            return result
        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            return []
    
    def get_security_info(self, stock_code: str) -> Dict:
        """
        获取证券基本信息
        
        :param stock_code: 证券代码
        :return: 证券信息字典
        """
        if not MINIQMT_AVAILABLE:
            return {}
        
        try:
            info = xtdata.get_instrument_detail(stock_code)
            return {
                'code': stock_code,
                'name': info['InstrumentName'],
                'market': info['ExchangeID'],
                'pre_close': info['PreClosePrice'],
                'upper_limit': info['HighLimitPrice'],
                'lower_limit': info['LowLimitPrice']
            }
        except Exception as e:
            logger.error(f"获取证券信息失败 {stock_code}: {e}")
            return {}
    
    def get_current_data(self, stock_code: str) -> Dict:
        """
        获取当前实时数据
        
        :param stock_code: 证券代码
        :return: 当前数据字典
        """
        if not MINIQMT_AVAILABLE:
            return {}
        
        try:
            # 获取当前快照数据
            data = xtdata.get_full_tick([stock_code])
            if stock_code in data:
                tick = data[stock_code]
                return {
                    'code': stock_code,
                    'datetime': tick['dateTime'],
                    'open': tick['open'],
                    'high': tick['high'],
                    'low': tick['low'],
                    'close': tick['lastPrice'],
                    'volume': tick['volume'],
                    'amount': tick['amount'],
                    'bid_price': tick['bidPrice1'],
                    'ask_price': tick['askPrice1'],
                    'bid_volume': tick['bidVol1'],
                    'ask_volume': tick['askVol1']
                }
        except Exception as e:
            logger.error(f"获取实时数据失败 {stock_code}: {e}")
            return {}
    
    def get_history_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str, 
        period: str = '1d',
        callback_func=None
    ) -> pd.DataFrame:
        """
        获取历史数据
        
        :param stock_code: 证券代码
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :param period: 周期 ('1m', '5m', '1d' 等)
        :param callback_func: 进度回调函数
        :return: 历史数据 DataFrame
        """
        if not MINIQMT_AVAILABLE:
            return pd.DataFrame()
        
        try:
            # 转换日期格式
            start_time = f"{start_date} 00:00:00"
            end_time = f"{end_date} 23:59:59"
            
            # 获取历史数据
            data = xtdata.get_market_data(
                stock_list=[stock_code],
                period=period,
                start_time=start_time,
                end_time=end_time,
                callback_func=callback_func
            )
            
            if stock_code in data:
                df = data[stock_code]
                
                # 重命名列以匹配现有格式
                column_mapping = {
                    'time': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume',
                    'amount': 'amount'
                }
                
                # 如果时间列存在，转换为日期格式
                if 'time' in df.columns:
                    df['date'] = pd.to_datetime(df['time'])
                    df = df.rename(columns=column_mapping)
                    
                # 确保列顺序一致
                required_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = None
                
                df = df[required_cols]
                df = df.sort_values('date').reset_index(drop=True)
                
                return df
            else:
                logger.warning(f"未获取到 {stock_code} 的历史数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取历史数据失败 {stock_code}: {e}")
            return pd.DataFrame()
    
    def subscribe_quote(self, stock_code: str, callback_func):
        """
        订阅实时行情
        
        :param stock_code: 证券代码
        :param callback_func: 回调函数
        """
        if not MINIQMT_AVAILABLE:
            return
        
        try:
            # 订阅实时行情
            xtdata.subscribe_quote(stock_code, callback=callback_func)
        except Exception as e:
            logger.error(f"订阅实时行情失败 {stock_code}: {e}")
    
    def unsubscribe_quote(self, stock_code: str):
        """
        取消订阅实时行情
        
        :param stock_code: 证券代码
        """
        if not MINIQMT_AVAILABLE:
            return
        
        try:
            # 取消订阅
            xtdata.unsubscribe_quote(stock_code)
        except Exception as e:
            logger.error(f"取消订阅实时行情失败 {stock_code}: {e}")


# 示例使用
if __name__ == "__main__":
    # 注意：要运行此示例，必须先安装 xtquant 库
    if MINIQMT_AVAILABLE:
        try:
            service = MiniQMTDataService()
            
            # 获取ETF列表
            etfs = service.get_etf_list()
            print(f"ETF数量: {len(etfs)}")
            if etfs:
                print(f"第一个ETF: {etfs[0]}")
            
            # 获取单个证券的实时数据
            if etfs:
                code = etfs[0]['code']
                current_data = service.get_current_data(code)
                print(f"实时数据: {current_data}")
                
                # 获取历史数据
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                hist_data = service.get_history_data(code, start_date, end_date)
                print(f"历史数据形状: {hist_data.shape}")
                
        except Exception as e:
            print(f"示例运行失败: {e}")
    else:
        print("xtquant 库不可用，请先安装")
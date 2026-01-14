import akshare as ak
import pandas as pd
import os
from loguru import logger
from datetime import datetime
# sd
class DataDownloader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_etf_list(self):
        """获取所有ETF列表"""
        logger.info("获取ETF列表...")
        try:
            etf_list = ak.fund_etf_category_sina(symbol="封闭式基金") # 这里可能需要根据实际需求调整，通常使用 fund_etf_spot_em 或类似接口
            # 使用更通用的东财接口获取实时行情以得到列表
            etf_list = ak.fund_etf_spot_em()
            return etf_list
        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            return pd.DataFrame()

    def download_kline(self, symbol, start_date="20210101", end_date=None):
        """下载日线数据"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        file_path = os.path.join(self.data_dir, f"{symbol}.parquet")
        
        existing_df = pd.DataFrame()
        if os.path.exists(file_path):
            existing_df = pd.read_parquet(file_path)
            if not existing_df.empty:
                # 获取最后日期
                last_date = pd.to_datetime(existing_df['date']).max()
                start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y%m%d")
                
                if start_date > end_date:
                    logger.info(f"{symbol} 数据已是最新")
                    return existing_df

        logger.info(f"下载 {symbol} 数据，从 {start_date} 到 {end_date}")
        try:
            # 使用 akshare 获取日线数据
            # 注意：不同标的可能需要不同的接口，ETF通常使用 fund_etf_hist_em
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            
            if df.empty:
                logger.warning(f"{symbol} 无新数据")
                return existing_df
            
            # 标准化列名
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_chg', 'change', 'turnover']
            
            if not existing_df.empty:
                df = pd.concat([existing_df, df]).drop_duplicates(subset=['date']).sort_values('date')
            
            df.to_parquet(file_path)
            return df
        except Exception as e:
            logger.error(f"下载 {symbol} 失败: {e}")
            return existing_df

if __name__ == "__main__":
    downloader = DataDownloader()
    # 测试下载一个ETF，例如 510300 (沪深300ETF)
    downloader.download_kline("510300")

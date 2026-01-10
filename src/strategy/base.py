import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, config):
        self.config = config
        self.name = config.get("name", "BaseStrategy")

    @abstractmethod
    def generate_signals(self, df):
        """生成交易信号"""
        pass

class MomentumStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.window = config.get("window", 20)
        self.threshold = config.get("threshold", 0.05)

    def generate_signals(self, df):
        """
        动量突破策略：
        如果过去 window 天的涨幅超过 threshold，则买入
        """
        df = df.copy()
        df['momentum'] = df['close'].pct_change(self.window)
        
        df['signal'] = 0
        df.loc[df['momentum'] > self.threshold, 'signal'] = 1
        df.loc[df['momentum'] < -self.threshold, 'signal'] = -1
        
        return df

class BacktestEngine:
    def __init__(self, initial_cash=100000, stop_loss_pct=0.05):
        self.initial_cash = initial_cash
        self.stop_loss_pct = stop_loss_pct

    def run(self, df):
        """
        简单的回测逻辑
        """
        cash = self.initial_cash
        position = 0
        df['equity'] = cash
        df['holdings'] = 0
        
        buy_price = 0
        
        for i in range(1, len(df)):
            current_price = df.iloc[i]['close']
            signal = df.iloc[i]['signal']
            
            # 止损判断
            if position > 0:
                if (current_price - buy_price) / buy_price < -self.stop_loss_pct:
                    cash = position * current_price
                    position = 0
                    buy_price = 0
            
            # 信号执行
            if signal == 1 and position == 0:
                # 买入
                position = cash / current_price
                buy_price = current_price
                cash = 0
            elif signal == -1 and position > 0:
                # 卖出
                cash = position * current_price
                position = 0
                buy_price = 0
                
            df.loc[df.index[i], 'equity'] = cash + (position * current_price)
            df.loc[df.index[i], 'holdings'] = position
            
        df['returns'] = df['equity'].pct_change()
        df['cum_returns'] = (1 + df['returns']).cumprod() - 1
        return df

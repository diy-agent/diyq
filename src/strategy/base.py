import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from loguru import logger


class Signal:
    """交易信号类"""
    BUY = 1
    SELL = -1
    HOLD = 0

    def __init__(self, signal_type: int, strength: float = 1.0, reason: str = ""):
        self.type = signal_type  # BUY, SELL, or HOLD
        self.strength = strength  # 信号强度 (0.0 - 1.0)
        self.reason = reason      # 信号产生原因


class BaseStrategy(ABC):
    """策略基类"""
    def __init__(self, config: Dict):
        self.config = config
        self.name = config.get("name", "BaseStrategy")
        self.symbol = config.get("symbol", "")
        self.position = 0  # 当前持仓
        self.cash = config.get("initial_cash", 100000)  # 当前现金
        self.total_value = self.cash  # 总资产价值

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        pass

    def update_position(self, price: float, signal: Signal):
        """更新持仓状态"""
        if signal.type == Signal.BUY and self.position <= 0:
            # 买入信号且当前为空仓或空头
            shares_to_buy = self.cash / price
            self.position += shares_to_buy
            self.cash -= shares_to_buy * price
        elif signal.type == Signal.SELL and self.position >= 0:
            # 卖出信号且当前为多仓或空仓
            proceeds = self.position * price
            self.cash += proceeds
            self.position = 0

    def get_portfolio_status(self) -> Dict:
        """获取投资组合状态"""
        return {
            "cash": self.cash,
            "position": self.position,
            "total_value": self.total_value
        }


class MomentumStrategy(BaseStrategy):
    """动量突破策略"""
    def __init__(self, config: Dict):
        super().__init__(config)
        self.window = config.get("window", 20)
        self.threshold = config.get("threshold", 0.05)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
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


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    def __init__(self, config: Dict):
        super().__init__(config)
        self.window = config.get("window", 20)
        self.std_multiplier = config.get("std_multiplier", 2.0)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        均值回归策略：
        当价格偏离移动平均线超过指定倍数的标准差时，做反向操作
        """
        df = df.copy()
        df['ma'] = df['close'].rolling(window=self.window).mean()
        df['std'] = df['close'].rolling(window=self.window).std()
        df['upper_band'] = df['ma'] + self.std_multiplier * df['std']
        df['lower_band'] = df['ma'] - self.std_multiplier * df['std']

        df['signal'] = 0
        df.loc[df['close'] > df['upper_band'], 'signal'] = -1  # 价格过高，卖出
        df.loc[df['close'] < df['lower_band'], 'signal'] = 1   # 价格过低，买入

        return df


class MovingAverageCrossoverStrategy(BaseStrategy):
    """移动平均线交叉策略"""
    def __init__(self, config: Dict):
        super().__init__(config)
        self.short_window = config.get("short_window", 10)
        self.long_window = config.get("long_window", 30)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        移动平均线交叉策略：
        短期均线上穿长期均线时买入，下穿时卖出
        """
        df = df.copy()
        df[f'ma_{self.short_window}'] = df['close'].rolling(window=self.short_window).mean()
        df[f'ma_{self.long_window}'] = df['close'].rolling(window=self.long_window).mean()

        # 生成交叉信号
        df['position'] = 0
        df.loc[df[f'ma_{self.short_window}'] > df[f'ma_{self.long_window}'], 'position'] = 1
        df.loc[df[f'ma_{self.short_window}'] < df[f'ma_{self.long_window}'], 'position'] = -1

        # 信号变化点
        df['signal'] = df['position'].diff()
        df.loc[df['signal'] > 0, 'signal'] = 1   # 买入信号
        df.loc[df['signal'] < 0, 'signal'] = -1  # 卖出信号

        return df


class StrategyManager:
    """策略管理器"""
    def __init__(self):
        self.strategies = {}
        self.active_strategies = []

    def register_strategy(self, name: str, strategy_class):
        """注册策略类"""
        self.strategies[name] = strategy_class

    def create_strategy(self, name: str, config: Dict) -> BaseStrategy:
        """创建策略实例"""
        if name not in self.strategies:
            raise ValueError(f"未知策略: {name}")

        return self.strategies[name](config)

    def run_strategy(self, strategy: BaseStrategy, data: pd.DataFrame) -> pd.DataFrame:
        """运行策略"""
        return strategy.generate_signals(data)

    def backtest_strategy(self, strategy: BaseStrategy, data: pd.DataFrame,
                         initial_cash: float = 100000,
                         commission_rate: float = 0.001) -> pd.DataFrame:
        """回测策略"""
        df = data.copy()
        df['signal'] = strategy.generate_signals(df)['signal']

        cash = initial_cash
        position = 0
        df['equity'] = initial_cash
        df['holdings'] = 0

        for i in range(1, len(df)):
            current_price = df.iloc[i]['close']
            signal = df.iloc[i]['signal']

            # 执行交易
            if signal == 1 and position == 0:  # 买入
                shares_to_buy = cash / current_price
                cost = shares_to_buy * current_price
                commission = cost * commission_rate
                if cash >= cost + commission:
                    position = shares_to_buy
                    cash -= (cost + commission)
            elif signal == -1 and position > 0:  # 卖出
                proceeds = position * current_price
                commission = proceeds * commission_rate
                cash += (proceeds - commission)
                position = 0

            df.loc[df.index[i], 'equity'] = cash + (position * current_price)
            df.loc[df.index[i], 'holdings'] = position

        df['returns'] = df['equity'].pct_change()
        df['cum_returns'] = (1 + df['returns']).cumprod() - 1
        return df


class BacktestEngine:
    """回测引擎"""
    def __init__(self, initial_cash=100000, stop_loss_pct=0.05, commission_rate=0.001):
        self.initial_cash = initial_cash
        self.stop_loss_pct = stop_loss_pct
        self.commission_rate = commission_rate

    def run(self, df: pd.DataFrame, strategy: BaseStrategy = None):
        """
        运行回测
        """
        df = df.copy()

        # 如果提供了策略，使用策略的信号，否则假设df中已有signal列
        if strategy:
            df = strategy.generate_signals(df)

        cash = self.initial_cash
        position = 0
        df['equity'] = cash
        df['holdings'] = 0
        df['trades'] = 0  # 记录交易次数

        buy_price = 0

        for i in range(1, len(df)):
            current_price = df.iloc[i]['close']
            signal = df.iloc[i]['signal'] if 'signal' in df.columns else 0

            # 止损判断
            if position > 0:
                if (current_price - buy_price) / buy_price < -self.stop_loss_pct:
                    proceeds = position * current_price
                    commission = proceeds * self.commission_rate
                    cash = proceeds - commission
                    position = 0
                    buy_price = 0
                    df.loc[df.index[i], 'trades'] += 1

            # 信号执行
            if signal == 1 and position == 0:  # 买入
                shares_to_buy = cash / current_price
                cost = shares_to_buy * current_price
                commission = cost * self.commission_rate
                if cash >= cost + commission:
                    position = shares_to_buy
                    buy_price = current_price
                    cash -= (cost + commission)
                    df.loc[df.index[i], 'trades'] += 1
            elif signal == -1 and position > 0:  # 卖出
                proceeds = position * current_price
                commission = proceeds * self.commission_rate
                cash = cash + proceeds - commission
                position = 0
                buy_price = 0
                df.loc[df.index[i], 'trades'] += 1

            df.loc[df.index[i], 'equity'] = cash + (position * current_price)
            df.loc[df.index[i], 'holdings'] = position

        df['returns'] = df['equity'].pct_change()
        df['cum_returns'] = (1 + df['returns']).cumprod() - 1

        # 计算回测指标
        total_return = (df['equity'].iloc[-1] / df['equity'].iloc[0]) - 1
        max_drawdown = (df['equity'] / df['equity'].expanding().max() - 1).min()
        volatility = df['returns'].std() * np.sqrt(252)  # 年化波动率
        sharpe_ratio = (df['returns'].mean() * 252) / volatility if volatility != 0 else 0

        metrics = {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'final_equity': df['equity'].iloc[-1],
            'trade_count': df['trades'].sum()
        }

        return df, metrics

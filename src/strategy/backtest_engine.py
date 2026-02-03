"""
高级回测引擎
提供更详细的回测分析和可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger

from .base import BaseStrategy, BacktestEngine


class AdvancedBacktestEngine:
    """高级回测引擎"""
    
    def __init__(self, initial_cash: float = 100000, 
                 commission_rate: float = 0.001, 
                 slippage_rate: float = 0.0005,
                 risk_free_rate: float = 0.03):
        """
        初始化高级回测引擎
        
        :param initial_cash: 初始资金
        :param commission_rate: 手续费率
        :param slippage_rate: 滑点率
        :param risk_free_rate: 无风险利率
        """
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.risk_free_rate = risk_free_rate
        self.results = {}
        self.metrics = {}

    def run_backtest(self, 
                     data: pd.DataFrame, 
                     strategy: BaseStrategy, 
                     start_date: str = None, 
                     end_date: str = None) -> Tuple[pd.DataFrame, Dict]:
        """
        运行回测
        
        :param data: 历史数据
        :param strategy: 策略实例
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: (回测结果数据框, 评估指标字典)
        """
        # 数据预处理
        df = data.copy()
        
        # 日期过滤
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        
        if df.empty:
            raise ValueError("回测数据为空")
        
        # 生成交易信号
        df = strategy.generate_signals(df)
        
        # 初始化账户变量
        cash = self.initial_cash
        position = 0
        avg_cost = 0  # 持仓均价
        df['cash'] = np.nan
        df['position'] = np.nan
        df['avg_cost'] = np.nan
        df['equity'] = np.nan
        df['total_value'] = np.nan
        df['return'] = np.nan
        df['benchmark_return'] = np.nan
        df['drawdown'] = np.nan
        df['trade_log'] = None
        
        # 计算基准收益（买入持有）
        df['benchmark_return'] = df['close'].pct_change()
        
        # 执行回测逻辑
        trade_log = []  # 记录交易详情
        
        for i in range(len(df)):
            current_bar = df.iloc[i]
            current_price = current_bar['close']
            signal = current_bar['signal'] if 'signal' in df.columns else 0
            
            # 记录当前状态
            df.iloc[i, df.columns.get_loc('cash')] = cash
            df.iloc[i, df.columns.get_loc('position')] = position
            df.iloc[i, df.columns.get_loc('avg_cost')] = avg_cost
            
            # 执行交易
            if signal != 0:
                executed, exec_price, exec_qty, fee = self._execute_trade(
                    cash, position, current_price, signal, avg_cost
                )
                
                if executed:
                    cash = exec_price
                    position = exec_qty
                    avg_cost = fee  # 在_execute_trade中返回的是新的平均成本
                    
                    # 记录交易
                    trade_log.append({
                        'date': current_bar['date'],
                        'action': 'BUY' if signal == 1 else 'SELL',
                        'price': current_price,
                        'quantity': abs(exec_qty),
                        'fee': fee
                    })
            
            # 计算总资产价值
            total_value = cash + position * current_price
            df.iloc[i, df.columns.get_loc('total_value')] = total_value
            df.iloc[i, df.columns.get_loc('equity')] = total_value
            
            # 计算当日收益率
            if i > 0:
                prev_total = df.iloc[i-1]['total_value']
                if prev_total != 0:
                    df.iloc[i, df.columns.get_loc('return')] = (total_value - prev_total) / prev_total
        
        # 计算累计收益率和回撤
        df['cum_return'] = (1 + df['return']).cumprod() - 1
        df['benchmark_cum_return'] = (1 + df['benchmark_return']).cumprod() - 1
        
        # 计算回撤
        rolling_max = df['total_value'].expanding().max()
        df['drawdown'] = (df['total_value'] - rolling_max) / rolling_max
        
        # 计算回测指标
        self.metrics = self._calculate_metrics(df, trade_log)
        
        # 保存结果
        self.results = {
            'data': df,
            'trades': trade_log,
            'metrics': self.metrics
        }
        
        return df, self.metrics

    def _execute_trade(self, cash: float, position: float, price: float, 
                      signal: int, avg_cost: float) -> Tuple[bool, float, float, float]:
        """
        执行交易
        
        :return: (是否执行, 新现金余额, 新持仓数量, 新平均成本)
        """
        # 考虑滑点
        exec_price = price * (1 + self.slippage_rate) if signal == 1 else price * (1 - self.slippage_rate)
        
        if signal == 1:  # 买入
            if position >= 0:  # 原本持有多头或空仓
                # 计算可购买数量
                total_cost = cash
                fee = total_cost * self.commission_rate
                net_cost = total_cost - fee
                qty = net_cost / exec_price
                
                new_position = position + qty
                if position > 0:
                    # 加仓，重新计算平均成本
                    new_avg_cost = (position * avg_cost + qty * exec_price) / new_position
                else:
                    # 开多仓
                    new_avg_cost = exec_price
                
                new_cash = cash - (qty * exec_price) - fee
                return True, new_cash, new_position, new_avg_cost
            else:  # 原本持有空头，平空
                # 平空操作
                cover_qty = min(abs(position), cash / exec_price)
                proceeds = cover_qty * exec_price
                fee = proceeds * self.commission_rate
                new_cash = cash + proceeds - fee
                new_position = position + cover_qty
                new_avg_cost = avg_cost if new_position != 0 else 0
                
                return True, new_cash, new_position, new_avg_cost
                
        elif signal == -1:  # 卖出
            if position > 0:  # 原本持有多头，卖出
                # 全部卖出
                proceeds = position * exec_price
                fee = proceeds * self.commission_rate
                new_cash = cash + proceeds - fee
                new_position = 0
                new_avg_cost = 0
                
                return True, new_cash, new_position, new_avg_cost
            else:  # 原本空仓或持有空头，开空或加空
                # 这里简化处理，不考虑做空
                return False, cash, position, avg_cost
        
        return False, cash, position, avg_cost

    def _calculate_metrics(self, df: pd.DataFrame, trade_log: List) -> Dict:
        """计算回测指标"""
        total_return = df['cum_return'].iloc[-1] if not df['cum_return'].empty else 0
        total_trades = len(trade_log)
        win_trades = sum(1 for trade in trade_log if 
                        trade['action'] == 'SELL' and df[df['date'] >= trade['date']]['close'].iloc[0] > trade.get('entry_price', trade['price']))
        
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        
        # 年化收益率
        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
        years = max(days / 365.0, 0.1)  # 至少0.1年
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 波动率
        daily_returns = df['return'].dropna()
        volatility = daily_returns.std() * np.sqrt(252)  # 年化波动率
        
        # 夏普比率
        excess_return = annual_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility != 0 else 0
        
        # 最大回撤
        rolling_max = df['total_value'].expanding().max()
        drawdowns = (df['total_value'] - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # 最大连续盈利/亏损
        positive_returns = daily_returns[daily_returns > 0]
        negative_returns = daily_returns[daily_returns < 0]
        max_consecutive_wins = len(positive_returns)  # 简化计算
        max_consecutive_losses = len(negative_returns)  # 简化计算
        
        # 超额收益（相对于基准）
        strategy_return = total_return
        benchmark_return = df['benchmark_cum_return'].iloc[-1] if not df['benchmark_cum_return'].empty else 0
        alpha = strategy_return - benchmark_return
        
        # Beta (相对于基准的敏感性)
        benchmark_returns = df['benchmark_return'].dropna()
        if len(daily_returns) > 1 and len(benchmark_returns) > 1:
            covariance = np.cov(daily_returns, benchmark_returns)[0][1]
            benchmark_var = np.var(benchmark_returns)
            beta = covariance / benchmark_var if benchmark_var != 0 else 0
        else:
            beta = 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'alpha': alpha,
            'beta': beta,
            'final_equity': df['total_value'].iloc[-1],
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'profit_factor': self._calculate_profit_factor(trade_log)
        }

    def _calculate_profit_factor(self, trade_log: List) -> float:
        """计算盈亏因子"""
        gains = sum(trade['pnl'] for trade in trade_log if trade.get('pnl', 0) > 0)
        losses = abs(sum(trade['pnl'] for trade in trade_log if trade.get('pnl', 0) < 0))
        return gains / losses if losses != 0 else float('inf')

    def plot_results(self, figsize=(15, 10)) -> plt.Figure:
        """绘制回测结果图表"""
        if not self.results:
            logger.warning("没有回测结果可绘制")
            return None
        
        df = self.results['data']
        fig, axes = plt.subplots(3, 1, figsize=figsize)
        
        # 净值曲线
        ax1 = axes[0]
        ax1.plot(df['date'], df['total_value'], label='策略净值', linewidth=2)
        ax1.plot(df['date'], df['close'] / df['close'].iloc[0] * self.initial_cash, label='基准(B&H)', linestyle='--')
        ax1.set_title('净值曲线对比')
        ax1.legend()
        ax1.grid(True)
        
        # 收益率对比
        ax2 = axes[1]
        ax2.plot(df['date'], df['cum_return'], label='策略累计收益率', linewidth=2)
        ax2.plot(df['date'], df['benchmark_cum_return'], label='基准累计收益率', linestyle='--')
        ax2.set_title('累计收益率对比')
        ax2.legend()
        ax2.grid(True)
        
        # 回撤曲线
        ax3 = axes[2]
        ax3.fill_between(df['date'], df['drawdown'], 0, alpha=0.3, color='red', label='回撤')
        ax3.set_title('回撤曲线')
        ax3.legend()
        ax3.grid(True)
        
        plt.tight_layout()
        return fig

    def get_report(self) -> str:
        """生成回测报告文本"""
        if not self.metrics:
            return "没有回测结果"
        
        metrics = self.metrics
        report = f"""
=== 量化策略回测报告 ===

基础指标:
- 总收益率: {metrics['total_return']:.2%}
- 年化收益率: {metrics['annual_return']:.2%}
- 最终净值: {metrics['final_equity']:.2f}
- 总交易次数: {metrics['total_trades']}
- 胜率: {metrics['win_rate']:.2%}

风险指标:
- 波动率: {metrics['volatility']:.2%}
- 最大回撤: {metrics['max_drawdown']:.2%}
- 夏普比率: {metrics['sharpe_ratio']:.2f}
- Beta: {metrics['beta']:.2f}
- Alpha: {metrics['alpha']:.2%}

其他指标:
- 盈亏因子: {metrics['profit_factor']:.2f}
- 最大连续盈利次数: {metrics['max_consecutive_wins']}
- 最大连续亏损次数: {metrics['max_consecutive_losses']}

========================
        """
        return report


# 多策略比较回测器
class MultiStrategyBacktester:
    """多策略比较回测器"""

    def __init__(self, initial_cash: float = 100000):
        self.initial_cash = initial_cash
        self.engines = {}
        self.strategies = {}
        self.results = {}

    def add_strategy(self, name: str, strategy: BaseStrategy):
        """添加策略"""
        self.engines[name] = AdvancedBacktestEngine(initial_cash=self.initial_cash)
        self.strategies[name] = strategy
        self.results[name] = None

    def run_all(self, data: pd.DataFrame, start_date: str = None, end_date: str = None) -> Dict:
        """运行所有策略的回测"""
        for name in self.strategies.keys():
            engine = self.engines[name]
            strategy = self.strategies[name]
            df_result, metrics = engine.run_backtest(data, strategy, start_date, end_date)
            self.results[name] = {
                'data': df_result,
                'metrics': metrics
            }

        return self.results

    def compare_results(self) -> pd.DataFrame:
        """比较各策略结果"""
        comparison_data = []
        for name, result in self.results.items():
            if result and 'metrics' in result:
                metrics = result['metrics']
                comparison_data.append({
                    'Strategy': name,
                    'Total Return': metrics['total_return'],
                    'Annual Return': metrics['annual_return'],
                    'Sharpe Ratio': metrics['sharpe_ratio'],
                    'Max Drawdown': metrics['max_drawdown'],
                    'Win Rate': metrics['win_rate'],
                    'Total Trades': metrics['total_trades']
                })

        if comparison_data:
            return pd.DataFrame(comparison_data)
        else:
            return pd.DataFrame()
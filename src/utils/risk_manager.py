"""
风险管理模块
提供仓位管理、风险控制和资金管理功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from loguru import logger
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM


class RiskManager:
    """风险管理器"""
    
    def __init__(self, 
                 max_portfolio_risk: float = 0.02,  # 最大组合风险（每日）
                 max_position_risk: float = 0.01,   # 最大单仓风险（每日）
                 max_drawdown: float = 0.15,        # 最大回撤
                 stop_loss_pct: float = 0.08,       # 止损百分比
                 take_profit_pct: float = 0.15):    # 止盈百分比
        """
        初始化风险管理器
        
        :param max_portfolio_risk: 最大组合风险（每日）
        :param max_position_risk: 最大单仓风险（每日）
        :param max_drawdown: 最大回撤限制
        :param stop_loss_pct: 止损百分比
        :param take_profit_pct: 止盈百分比
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_risk = max_position_risk
        self.max_drawdown = max_drawdown
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        
        self.positions: Dict[str, Position] = {}
        self.portfolio_value = 0.0
        self.initial_capital = 0.0
        self.daily_pnl = 0.0
        self.max_portfolio_value = 0.0
        self.current_drawdown = 0.0
        self.risk_limits_breached = False
    
    def set_initial_capital(self, capital: float):
        """设置初始资本"""
        self.initial_capital = capital
        self.portfolio_value = capital
        self.max_portfolio_value = capital
    
    def update_portfolio_value(self, value: float):
        """更新组合价值"""
        self.portfolio_value = value
        if value > self.max_portfolio_value:
            self.max_portfolio_value = value
        
        # 计算当前回撤
        self.current_drawdown = (self.max_portfolio_value - value) / self.max_portfolio_value
    
    def add_position(self, symbol: str, quantity: float, entry_price: float):
        """添加持仓"""
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            unrealized_pnl=0.0
        )
        self.positions[symbol] = position
    
    def update_position(self, symbol: str, current_price: float):
        """更新持仓信息"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        position.current_price = current_price
        position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
    
    def close_position(self, symbol: str, exit_price: float, quantity: float = None):
        """平仓"""
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if quantity is None or quantity >= position.quantity:
            # 全部平仓
            realized_pnl = (exit_price - position.entry_price) * position.quantity
            position.realized_pnl += realized_pnl
            del self.positions[symbol]
        else:
            # 部分平仓
            realized_pnl = (exit_price - position.entry_price) * quantity
            position.realized_pnl += realized_pnl
            position.quantity -= quantity
        
        return True
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              risk_per_trade: float = None) -> float:
        """
        计算仓位大小（基于风险）
        
        :param symbol: 证券代码
        :param entry_price: 入场价格
        :param risk_per_trade: 单笔交易风险金额
        :return: 建议仓位大小
        """
        if risk_per_trade is None:
            # 默认风险为总资金的0.1%
            risk_per_trade = self.portfolio_value * 0.001
        
        # 计算止损价差
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
        
        # 基于风险计算仓位
        position_size = risk_per_trade / risk_per_share
        
        # 检查是否超过单仓风险限制
        position_value = position_size * entry_price
        if position_value > self.portfolio_value * self.max_position_risk:
            position_size = (self.portfolio_value * self.max_position_risk) / entry_price
        
        return min(position_size, self.portfolio_value / entry_price)  # 不超过总资金
    
    def check_risk_limits(self, symbol: str = None) -> Tuple[bool, str]:
        """
        检查风险限制
        
        :param symbol: 证券代码（可选，如果不提供则检查整个组合）
        :return: (是否通过检查, 原因)
        """
        # 检查最大回撤
        if self.current_drawdown > self.max_drawdown:
            return False, f"超出最大回撤限制: {self.current_drawdown:.2%} > {self.max_drawdown:.2%}"
        
        # 检查单仓风险
        if symbol and symbol in self.positions:
            position = self.positions[symbol]
            position_value = position.quantity * position.current_price
            position_risk = abs(position.unrealized_pnl) / self.portfolio_value
            
            if position_risk > self.max_position_risk:
                return False, f"{symbol} 超出单仓风险限制: {position_risk:.2%} > {self.max_position_risk:.2%}"
        
        # 检查组合风险
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        portfolio_risk = abs(total_unrealized_pnl) / self.portfolio_value
        if portfolio_risk > self.max_portfolio_risk:
            return False, f"超出组合风险限制: {portfolio_risk:.2%} > {self.max_portfolio_risk:.2%}"
        
        return True, "风险检查通过"
    
    def should_exit_position(self, symbol: str) -> Tuple[bool, str]:
        """
        检查是否应该平仓
        
        :param symbol: 证券代码
        :return: (是否应该平仓, 原因)
        """
        if symbol not in self.positions:
            return False, "无此持仓"
        
        position = self.positions[symbol]
        pnl_pct = (position.current_price - position.entry_price) / position.entry_price
        
        # 止损检查
        if pnl_pct <= -self.stop_loss_pct:
            return True, f"达到止损条件: {pnl_pct:.2%} <= -{self.stop_loss_pct:.2%}"
        
        # 止盈检查
        if pnl_pct >= self.take_profit_pct:
            return True, f"达到止盈条件: {pnl_pct:.2%} >= {self.take_profit_pct:.2%}"
        
        # 风险检查
        risk_check, risk_msg = self.check_risk_limits(symbol)
        if not risk_check:
            return True, f"风险控制触发: {risk_msg}"
        
        return False, "无需平仓"
    
    def get_portfolio_risk_summary(self) -> Dict:
        """获取组合风险摘要"""
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        total_realized_pnl = sum(p.realized_pnl for p in self.positions.values())
        total_value = sum(p.quantity * p.current_price for p in self.positions.values())
        
        position_risks = {}
        for symbol, position in self.positions.items():
            position_risks[symbol] = {
                'pnl_pct': (position.current_price - position.entry_price) / position.entry_price,
                'position_value': position.quantity * position.current_price,
                'risk_contribution': abs(position.unrealized_pnl) / self.portfolio_value if self.portfolio_value > 0 else 0
            }
        
        return {
            'total_positions': len(self.positions),
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_value': total_value,
            'portfolio_value': self.portfolio_value,
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'position_risks': position_risks,
            'risk_limits_breached': self.risk_limits_breached
        }


class VaRManager:
    """VaR (风险价值) 管理器"""
    
    def __init__(self, confidence_level: float = 0.95, lookback_days: int = 252):
        """
        初始化VaR管理器
        
        :param confidence_level: 置信水平
        :param lookback_days: 回溯天数
        """
        self.confidence_level = confidence_level
        self.lookback_days = lookback_days
        self.price_history = {}
        self.return_history = {}
    
    def update_price_history(self, symbol: str, price: float, timestamp=None):
        """更新价格历史"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.return_history[symbol] = []
        
        self.price_history[symbol].append((timestamp or pd.Timestamp.now(), price))
        
        # 维护固定长度的历史记录
        if len(self.price_history[symbol]) > self.lookback_days + 1:
            self.price_history[symbol] = self.price_history[symbol][-self.lookback_days-1:]
        
        # 计算收益率
        prices = [p[1] for p in self.price_history[symbol]]
        if len(prices) > 1:
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            self.return_history[symbol] = returns[-self.lookback_days:]
    
    def calculate_var(self, symbol: str, portfolio_value: float, weights: List[float] = None) -> float:
        """
        计算VaR
        
        :param symbol: 证券代码
        :param portfolio_value: 组合价值
        :param weights: 权重（对于多资产组合）
        :return: VaR值
        """
        if symbol not in self.return_history or len(self.return_history[symbol]) < 10:
            return 0.0  # 历史数据不足
        
        returns = self.return_history[symbol]
        
        # 计算VaR (历史模拟法)
        var_percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(returns, var_percentile)
        
        # 转换为货币价值
        var_value = abs(var_return) * portfolio_value
        
        return var_value
    
    def calculate_expected_shortfall(self, symbol: str, portfolio_value: float) -> float:
        """
        计算预期短缺 (Expected Shortfall)
        
        :param symbol: 证券代码
        :param portfolio_value: 组合价值
        :return: 预期短缺值
        """
        if symbol not in self.return_history or len(self.return_history[symbol]) < 10:
            return 0.0
        
        returns = np.array(self.return_history[symbol])
        var_percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(returns, var_percentile)
        
        # 计算所有低于VaR的收益率的平均值
        tail_returns = returns[returns <= var_return]
        if len(tail_returns) == 0:
            return 0.0
        
        es_return = np.mean(tail_returns)
        es_value = abs(es_return) * portfolio_value
        
        return es_value


class PortfolioOptimizer:
    """投资组合优化器"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """计算夏普比率"""
        if len(returns) < 2 or returns.std() == 0:
            return 0.0
        
        excess_return = returns.mean() * 252 - self.risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        
        return excess_return / volatility if volatility != 0 else 0.0
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """计算最大回撤"""
        if len(equity_curve) < 2:
            return 0.0
        
        rolling_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        
        return drawdowns.min()
    
    def optimize_weights(self, returns_data: Dict[str, pd.Series], 
                        method: str = 'sharpe') -> Dict[str, float]:
        """
        优化资产权重
        
        :param returns_data: 各资产的收益率数据
        :param method: 优化方法 ('sharpe', 'min_volatility', 'equal')
        :return: 优化后的权重
        """
        if method == 'equal':
            # 等权重分配
            symbols = list(returns_data.keys())
            weight = 1.0 / len(symbols)
            return {symbol: weight for symbol in symbols}
        
        elif method == 'sharpe':
            # 基于夏普比率的权重分配
            sharpe_ratios = {}
            for symbol, returns in returns_data.items():
                sharpe_ratios[symbol] = self.calculate_sharpe_ratio(returns)
            
            # 归一化夏普比率作为权重
            total_sharpe = sum(max(0, sr) for sr in sharpe_ratios.values())  # 只考虑正夏普比率
            if total_sharpe == 0:
                # 如果所有夏普比率都是负的，使用等权重
                symbols = list(returns_data.keys())
                weight = 1.0 / len(symbols)
                return {symbol: weight for symbol in symbols}
            
            weights = {}
            for symbol, sharpe in sharpe_ratios.items():
                weights[symbol] = max(0, sharpe) / total_sharpe if total_sharpe != 0 else 0
            
            return weights
        
        else:
            # 默认使用等权重
            symbols = list(returns_data.keys())
            weight = 1.0 / len(symbols)
            return {symbol: weight for symbol in symbols}


# 示例使用
if __name__ == "__main__":
    # 创建风险管理器
    risk_manager = RiskManager(
        max_portfolio_risk=0.02,
        max_position_risk=0.01,
        max_drawdown=0.15,
        stop_loss_pct=0.08,
        take_profit_pct=0.15
    )
    
    risk_manager.set_initial_capital(100000)
    risk_manager.update_portfolio_value(95000)  # 模拟组合价值下降
    
    # 添加持仓
    risk_manager.add_position("000001.SZ", 1000, 10.0)
    risk_manager.update_position("000001.SZ", 9.5)  # 价格下跌
    
    # 检查风险
    is_ok, msg = risk_manager.check_risk_limits("000001.SZ")
    print(f"风险检查: {msg}")
    
    should_exit, exit_reason = risk_manager.should_exit_position("000001.SZ")
    print(f"是否应平仓: {exit_reason}")
    
    # 获取风险摘要
    summary = risk_manager.get_portfolio_risk_summary()
    print(f"组合风险摘要: {summary}")
    
    # VaR 示例
    var_manager = VaRManager(confidence_level=0.95, lookback_days=252)
    for i in range(100):
        var_manager.update_price_history("000001.SZ", 10 + np.random.normal(0, 0.1))
    
    var_value = var_manager.calculate_var("000001.SZ", 100000)
    print(f"VaR (95%): {var_value:.2f}")
    
    # 投资组合优化示例
    optimizer = PortfolioOptimizer()
    returns_data = {
        "asset1": pd.Series(np.random.normal(0.001, 0.02, 252)),
        "asset2": pd.Series(np.random.normal(0.0015, 0.025, 252)),
        "asset3": pd.Series(np.random.normal(0.0005, 0.015, 252))
    }
    
    optimal_weights = optimizer.optimize_weights(returns_data, method='sharpe')
    print(f"优化权重: {optimal_weights}")
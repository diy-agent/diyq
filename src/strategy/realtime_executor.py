"""
实时策略执行器
使用 miniqmt 进行实时策略执行和交易
"""

import threading
import time
from typing import Dict, List
from loguru import logger
import pandas as pd

from .base import BaseStrategy, Signal, StrategyManager
from ..data.minqmt_data_service import MiniQMTDataService, MINIQMT_AVAILABLE


class RealTimeStrategyExecutor:
    """
    实时策略执行器
    负责接收实时数据、执行策略并下达交易指令
    """
    
    def __init__(self, account_id: str, miniqmt_path: str = None):
        """
        初始化实时策略执行器
        
        :param account_id: 交易账户ID
        :param miniqmt_path: miniqmt 安装路径
        """
        if not MINIQMT_AVAILABLE:
            raise ImportError(
                "xtquant 库未安装，无法使用实时策略执行器。请从券商获取安装包。"
            )
        
        self.account_id = account_id
        self.miniqmt_service = MiniQMTDataService(miniqmt_path)
        self.strategy_manager = StrategyManager()
        self.active_strategies = {}  # {symbol: strategy_instance}
        self.subscribed_symbols = set()
        self.running = False
        self.data_buffer = {}  # 存储每个股票的缓存数据
        
        # 注册内置策略
        self._register_builtin_strategies()
    
    def _register_builtin_strategies(self):
        """注册内置策略类型"""
        from .base import MomentumStrategy, MeanReversionStrategy, MovingAverageCrossoverStrategy
        
        self.strategy_manager.register_strategy("momentum", MomentumStrategy)
        self.strategy_manager.register_strategy("mean_reversion", MeanReversionStrategy)
        self.strategy_manager.register_strategy("ma_crossover", MovingAverageCrossoverStrategy)
    
    def add_strategy(self, symbol: str, strategy_name: str, config: Dict):
        """
        添加策略到指定股票
        
        :param symbol: 股票代码
        :param strategy_name: 策略名称
        :param config: 策略配置
        """
        config['symbol'] = symbol
        strategy = self.strategy_manager.create_strategy(strategy_name, config)
        self.active_strategies[symbol] = strategy
        
        # 如果还没有订阅该股票，开始订阅
        if symbol not in self.subscribed_symbols:
            self._subscribe_symbol(symbol)
    
    def remove_strategy(self, symbol: str):
        """
        移除指定股票的策略
        
        :param symbol: 股票代码
        """
        if symbol in self.active_strategies:
            del self.active_strategies[symbol]
        
        # 如果没有其他策略使用该股票，取消订阅
        if symbol in self.subscribed_symbols:
            other_symbols_using = [s for s, strat in self.active_strategies.items() if strat.symbol == symbol]
            if not other_symbols_using:
                self._unsubscribe_symbol(symbol)
    
    def _subscribe_symbol(self, symbol: str):
        """订阅股票实时数据"""
        try:
            self.miniqmt_service.subscribe_quote(symbol, self._on_quote_update)
            self.subscribed_symbols.add(symbol)
            logger.info(f"已订阅 {symbol} 的实时数据")
        except Exception as e:
            logger.error(f"订阅 {symbol} 实时数据失败: {e}")
    
    def _unsubscribe_symbol(self, symbol: str):
        """取消订阅股票实时数据"""
        try:
            self.miniqmt_service.unsubscribe_quote(symbol)
            self.subscribed_symbols.discard(symbol)
            logger.info(f"已取消订阅 {symbol} 的实时数据")
        except Exception as e:
            logger.error(f"取消订阅 {symbol} 实时数据失败: {e}")
    
    def _on_quote_update(self, data):
        """
        行情更新回调函数
        
        :param data: 行情数据
        """
        for stock_code, quote_data in data.items():
            if stock_code in self.active_strategies:
                # 更新数据缓存
                self._update_data_cache(stock_code, quote_data)
                
                # 执行策略
                self._execute_strategy_for_stock(stock_code)
    
    def _update_data_cache(self, symbol: str, quote_data: Dict):
        """更新数据缓存"""
        if symbol not in self.data_buffer:
            self.data_buffer[symbol] = []
        
        # 添加最新的行情数据
        self.data_buffer[symbol].append({
            'datetime': quote_data.get('dateTime'),
            'open': quote_data.get('open'),
            'high': quote_data.get('high'),
            'low': quote_data.get('low'),
            'close': quote_data.get('lastPrice'),
            'volume': quote_data.get('volume'),
            'amount': quote_data.get('amount')
        })
        
        # 限制缓存大小，保留最近的数据
        if len(self.data_buffer[symbol]) > 1000:  # 只保留最近1000条数据
            self.data_buffer[symbol] = self.data_buffer[symbol][-1000:]
    
    def _execute_strategy_for_stock(self, symbol: str):
        """为指定股票执行策略"""
        if symbol not in self.active_strategies:
            return
        
        strategy = self.active_strategies[symbol]
        
        # 构建DataFrame用于策略计算
        if symbol in self.data_buffer and len(self.data_buffer[symbol]) > 1:
            df = pd.DataFrame(self.data_buffer[symbol])
            
            try:
                # 执行策略获取信号
                df_with_signals = strategy.generate_signals(df)
                latest_signal = df_with_signals.iloc[-1]['signal']
                
                if latest_signal != 0:  # 有交易信号
                    signal_obj = Signal(latest_signal)
                    self._execute_trade(symbol, signal_obj)
            except Exception as e:
                logger.error(f"执行 {symbol} 策略时出错: {e}")
    
    def _execute_trade(self, symbol: str, signal: Signal):
        """
        执行交易
        
        :param symbol: 股票代码
        :param signal: 交易信号
        """
        try:
            # 这里应该调用 miniqmt 的交易接口
            # 由于实际交易接口需要账户验证等复杂流程，这里仅作示意
            current_data = self.miniqmt_service.get_current_data(symbol)
            current_price = current_data.get('close', 0)
            
            if signal.type == Signal.BUY:
                logger.info(f"执行买入 {symbol} 指令，价格: {current_price}")
                # TODO: 实际下单逻辑 (需要账户验证等)
                # order_id = self.place_order(symbol, 'buy', quantity, current_price)
            elif signal.type == Signal.SELL:
                logger.info(f"执行卖出 {symbol} 指令，价格: {current_price}")
                # TODO: 实际下单逻辑 (需要账户验证等)
                # order_id = self.place_order(symbol, 'sell', quantity, current_price)
            
            # 更新策略持仓
            strategy = self.active_strategies.get(symbol)
            if strategy:
                strategy.update_position(current_price, signal)
                
        except Exception as e:
            logger.error(f"执行 {symbol} 交易时出错: {e}")
    
    def start(self):
        """启动实时策略执行器"""
        if self.running:
            logger.warning("实时策略执行器已在运行中")
            return
        
        self.running = True
        logger.info("实时策略执行器已启动")
        
        # 启动主循环线程
        self.main_thread = threading.Thread(target=self._main_loop)
        self.main_thread.daemon = True
        self.main_thread.start()
    
    def stop(self):
        """停止实时策略执行器"""
        self.running = False
        
        # 取消所有订阅
        for symbol in list(self.subscribed_symbols):
            self._unsubscribe_symbol(symbol)
        
        logger.info("实时策略执行器已停止")
    
    def _main_loop(self):
        """主循环"""
        while self.running:
            time.sleep(0.1)  # 防止CPU占用过高
    
    def get_portfolio_status(self) -> Dict:
        """获取整体投资组合状态"""
        total_value = 0
        cash = 0
        positions = {}
        
        for symbol, strategy in self.active_strategies.items():
            status = strategy.get_portfolio_status()
            cash += status['cash']
            
            # 获取当前市场价格计算持仓价值
            current_data = self.miniqmt_service.get_current_data(symbol)
            current_price = current_data.get('close', 0)
            position_value = status['position'] * current_price
            total_value += status['cash'] + position_value
            
            positions[symbol] = {
                'position': status['position'],
                'market_value': position_value,
                'avg_cost': getattr(strategy, 'avg_cost', 0),
                'unrealized_pnl': position_value - (status['position'] * getattr(strategy, 'avg_cost', 0))
            }
        
        return {
            'total_value': total_value,
            'cash': cash,
            'positions': positions,
            'strategies_count': len(self.active_strategies)
        }


# 示例使用
if __name__ == "__main__":
    if MINIQMT_AVAILABLE:
        try:
            # 创建执行器实例 (注意：需要真实的账户ID)
            executor = RealTimeStrategyExecutor(account_id="your_account_id")
            
            # 添加动量策略到某个股票
            momentum_config = {
                "name": "MomentumStrategy",
                "window": 10,
                "threshold": 0.03,
                "initial_cash": 50000
            }
            executor.add_strategy("000001.SZ", "momentum", momentum_config)
            
            # 启动执行器
            executor.start()
            
            # 运行一段时间后停止
            time.sleep(60)
            executor.stop()
            
        except Exception as e:
            print(f"示例运行失败: {e}")
    else:
        print("xtquant 库不可用，请先安装")
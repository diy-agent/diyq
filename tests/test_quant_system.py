"""
量化交易系统测试用例
测试各个模块的功能和集成
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.data.downloader import DataDownloader
from src.data.miniqmt_data_service import MiniQMTDataService, MINIQMT_AVAILABLE
from src.strategy.base import (
    BaseStrategy, MomentumStrategy, MeanReversionStrategy, 
    MovingAverageCrossoverStrategy, StrategyManager, BacktestEngine
)
from src.strategy.backtest_engine import AdvancedBacktestEngine, MultiStrategyBacktester
from src.utils.risk_manager import RiskManager, VaRManager, PortfolioOptimizer
from src.trading.execution_interface import (
    Order, OrderSide, OrderType, OrderStatus,
    PaperTradingBroker, ExecutionManager
)


class TestDataDownloader(unittest.TestCase):
    """测试数据下载器"""
    
    def setUp(self):
        self.downloader = DataDownloader(data_dir="test_data")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.downloader.data_dir, "test_data")
    
    def test_get_etf_list(self):
        """测试获取ETF列表"""
        # 由于依赖外部数据源，这里只测试方法是否存在
        self.assertTrue(hasattr(self.downloader, 'get_etf_list'))
    
    def test_download_kline(self):
        """测试下载K线数据"""
        # 由于依赖外部数据源，这里只测试方法是否存在
        self.assertTrue(hasattr(self.downloader, 'download_kline'))


class TestStrategies(unittest.TestCase):
    """测试策略"""
    
    def setUp(self):
        # 创建测试数据
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 10 + np.cumsum(np.random.randn(100) * 0.1)
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000000, 2000000, 100),
            'amount': prices * np.random.randint(1000000, 2000000, 100)
        })
        
        self.momentum_config = {
            "name": "TestMomentum",
            "window": 10,
            "threshold": 0.02,
            "initial_cash": 100000
        }
        
        self.mean_reversion_config = {
            "name": "TestMeanReversion",
            "window": 20,
            "std_multiplier": 2.0,
            "initial_cash": 100000
        }
        
        self.ma_crossover_config = {
            "name": "TestMACrossover",
            "short_window": 5,
            "long_window": 20,
            "initial_cash": 100000
        }
    
    def test_momentum_strategy(self):
        """测试动量策略"""
        strategy = MomentumStrategy(self.momentum_config)
        result = strategy.generate_signals(self.test_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('signal', result.columns)
        self.assertIn('momentum', result.columns)
        # 检查信号值是否在合理范围内
        self.assertTrue(all(result['signal'].isin([1, 0, -1])))
    
    def test_mean_reversion_strategy(self):
        """测试均值回归策略"""
        strategy = MeanReversionStrategy(self.mean_reversion_config)
        result = strategy.generate_signals(self.test_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('signal', result.columns)
        self.assertIn('ma', result.columns)
        self.assertIn('upper_band', result.columns)
        self.assertIn('lower_band', result.columns)
        # 检查信号值是否在合理范围内
        self.assertTrue(all(result['signal'].isin([1, 0, -1])))
    
    def test_ma_crossover_strategy(self):
        """测试移动平均线交叉策略"""
        strategy = MovingAverageCrossoverStrategy(self.ma_crossover_config)
        result = strategy.generate_signals(self.test_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('signal', result.columns)
        self.assertIn('ma_5', result.columns)
        self.assertIn('ma_20', result.columns)
        # 检查信号值是否在合理范围内
        self.assertTrue(all(result['signal'].isin([1, 0, -1])))
    
    def test_strategy_manager(self):
        """测试策略管理器"""
        manager = StrategyManager()
        
        # 注册策略
        manager.register_strategy("momentum", MomentumStrategy)
        manager.register_strategy("mean_reversion", MeanReversionStrategy)
        
        # 创建策略实例
        momentum_strategy = manager.create_strategy("momentum", self.momentum_config)
        mean_rev_strategy = manager.create_strategy("mean_reversion", self.mean_reversion_config)
        
        self.assertIsInstance(momentum_strategy, MomentumStrategy)
        self.assertIsInstance(mean_rev_strategy, MeanReversionStrategy)
        
        # 运行策略
        momentum_result = manager.run_strategy(momentum_strategy, self.test_data)
        self.assertIsInstance(momentum_result, pd.DataFrame)


class TestBacktesting(unittest.TestCase):
    """测试回测引擎"""
    
    def setUp(self):
        # 创建测试数据
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        prices = 10 + np.cumsum(np.random.randn(100) * 0.1)
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000000, 2000000, 100),
            'amount': prices * np.random.randint(1000000, 2000000, 100)
        })
        
        self.momentum_config = {
            "name": "TestMomentum",
            "window": 10,
            "threshold": 0.02,
            "initial_cash": 100000
        }
    
    def test_basic_backtest_engine(self):
        """测试基础回测引擎"""
        engine = BacktestEngine(initial_cash=100000, stop_loss_pct=0.05)
        strategy = MomentumStrategy(self.momentum_config)
        
        result_df, metrics = engine.run(self.test_data, strategy)
        
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn('equity', result_df.columns)
        self.assertIn('cum_returns', result_df.columns)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_return', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('sharpe_ratio', metrics)
    
    def test_advanced_backtest_engine(self):
        """测试高级回测引擎"""
        engine = AdvancedBacktestEngine(initial_cash=100000)
        strategy = MomentumStrategy(self.momentum_config)
        
        result_df, metrics = engine.run_backtest(self.test_data, strategy)
        
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn('total_value', result_df.columns)
        self.assertIn('cum_return', result_df.columns)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_return', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('win_rate', metrics)
    
    def test_multi_strategy_backtester(self):
        """测试多策略回测器"""
        backtester = MultiStrategyBacktester(initial_cash=100000)
        
        # 添加多个策略
        momentum_strategy = MomentumStrategy(self.momentum_config)
        mean_rev_config = {
            "name": "TestMeanReversion",
            "window": 20,
            "std_multiplier": 2.0,
            "initial_cash": 100000
        }
        mean_rev_strategy = MeanReversionStrategy(mean_rev_config)
        
        backtester.add_strategy("momentum", momentum_strategy)
        backtester.add_strategy("mean_reversion", mean_rev_strategy)
        
        # 运行回测
        results = backtester.run_all(self.test_data)
        
        self.assertIsInstance(results, dict)
        self.assertIn("momentum", results)
        self.assertIn("mean_reversion", results)
        
        # 比较结果
        comparison = backtester.compare_results()
        self.assertIsInstance(comparison, pd.DataFrame)
        self.assertGreaterEqual(len(comparison), 2)  # 至少有两个策略


class TestRiskManagement(unittest.TestCase):
    """测试风险管理"""
    
    def test_risk_manager(self):
        """测试风险管理员"""
        risk_manager = RiskManager(
            max_portfolio_risk=0.02,
            max_position_risk=0.01,
            max_drawdown=0.15,
            stop_loss_pct=0.08,
            take_profit_pct=0.15
        )
        
        risk_manager.set_initial_capital(100000)
        risk_manager.update_portfolio_value(95000)  # 模拟亏损
        
        # 添加持仓
        risk_manager.add_position("000001.SZ", 1000, 10.0)
        risk_manager.update_position("000001.SZ", 9.5)  # 价格下跌
        
        # 检查风险
        is_ok, msg = risk_manager.check_risk_limits("000001.SZ")
        self.assertIsInstance(is_ok, bool)
        
        should_exit, exit_reason = risk_manager.should_exit_position("000001.SZ")
        self.assertIsInstance(should_exit, bool)
        
        # 获取风险摘要
        summary = risk_manager.get_portfolio_risk_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('total_positions', summary)
        self.assertIn('current_drawdown', summary)
    
    def test_var_manager(self):
        """测试VaR管理器"""
        var_manager = VaRManager(confidence_level=0.95, lookback_days=100)
        
        # 更新价格历史
        for i in range(100):
            price = 10 + np.random.normal(0, 0.1)
            var_manager.update_price_history("000001.SZ", price)
        
        # 计算VaR
        var_value = var_manager.calculate_var("000001.SZ", 100000)
        self.assertIsInstance(var_value, float)
        self.assertGreaterEqual(var_value, 0)
        
        # 计算预期短缺
        es_value = var_manager.calculate_expected_shortfall("000001.SZ", 100000)
        self.assertIsInstance(es_value, float)
        self.assertGreaterEqual(es_value, 0)
    
    def test_portfolio_optimizer(self):
        """测试投资组合优化器"""
        optimizer = PortfolioOptimizer()
        
        # 创建测试收益率数据
        np.random.seed(42)
        returns_data = {
            "asset1": pd.Series(np.random.normal(0.001, 0.02, 252)),
            "asset2": pd.Series(np.random.normal(0.0015, 0.025, 252)),
            "asset3": pd.Series(np.random.normal(0.0005, 0.015, 252))
        }
        
        # 计算夏普比率
        sharpe1 = optimizer.calculate_sharpe_ratio(returns_data["asset1"])
        self.assertIsInstance(sharpe1, float)
        
        # 计算最大回撤
        equity_curve = (1 + returns_data["asset1"]).cumprod() * 100000
        max_dd = optimizer.calculate_max_drawdown(equity_curve)
        self.assertIsInstance(max_dd, float)
        self.assertLessEqual(max_dd, 0)
        
        # 优化权重
        weights = optimizer.optimize_weights(returns_data, method='sharpe')
        self.assertIsInstance(weights, dict)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=7)


class TestExecutionInterface(unittest.TestCase):
    """测试交易执行接口"""
    
    def test_order_creation(self):
        """测试订单创建"""
        order = Order(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            order_type=OrderType.LIMIT,
            price=10.5
        )
        
        self.assertEqual(order.symbol, "000001.SZ")
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.quantity, 1000)
        self.assertEqual(order.order_type, OrderType.LIMIT)
        self.assertEqual(order.price, 10.5)
        self.assertEqual(order.status, OrderStatus.PENDING)
    
    def test_order_fill(self):
        """测试订单成交"""
        order = Order(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            order_type=OrderType.MARKET
        )
        
        # 部分成交
        order.fill(500, 10.5)
        self.assertEqual(order.filled_quantity, 500)
        self.assertEqual(order.average_fill_price, 10.5)
        self.assertEqual(order.status, OrderStatus.PARTIALLY_FILLED)
        
        # 完全成交
        order.fill(500, 10.6)
        expected_avg_price = (500 * 10.5 + 500 * 10.6) / 1000
        self.assertEqual(order.filled_quantity, 1000)
        self.assertAlmostEqual(order.average_fill_price, expected_avg_price, places=6)
        self.assertEqual(order.status, OrderStatus.FILLED)
    
    def test_paper_trading_broker(self):
        """测试模拟交易接口"""
        broker = PaperTradingBroker(initial_balance=100000)
        
        # 连接
        connected = broker.connect()
        self.assertTrue(connected)
        
        # 下单
        order = Order(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            order_type=OrderType.MARKET,
            price=10.0
        )
        
        order_id = broker.place_order(order)
        self.assertIsNotNone(order_id)
        
        # 检查订单状态
        retrieved_order = broker.get_order_status(order_id)
        self.assertIsNotNone(retrieved_order)
        
        # 获取账户信息
        account_info = broker.get_account_info()
        self.assertIsInstance(account_info, dict)
        self.assertIn('available_funds', account_info)
        
        # 获取持仓
        positions = broker.get_positions()
        self.assertIsInstance(positions, list)
        
        # 撤单（对已成交订单无效）
        cancelled = broker.cancel_order(order_id)
        # 对于已成交订单，撤单应该失败
        retrieved_order_after_cancel = broker.get_order_status(order_id)
        if retrieved_order_after_cancel.status == OrderStatus.FILLED:
            self.assertFalse(cancelled)
        
        # 断开连接
        disconnected = broker.disconnect()
        self.assertTrue(disconnected)
    
    def test_execution_manager(self):
        """测试执行管理器"""
        broker = PaperTradingBroker(initial_balance=100000)
        execution_manager = ExecutionManager(broker)
        
        # 执行订单
        order_id = execution_manager.execute_order(
            "000001.SZ", OrderSide.BUY, 1000, OrderType.MARKET
        )
        self.assertIsNotNone(order_id)
        
        # 执行信号
        signal_order_id = execution_manager.execute_signal("000001.SZ", 1, 500)
        self.assertIsNotNone(signal_order_id)
        
        # 获取状态
        status = execution_manager.get_execution_status(order_id)
        self.assertIsNotNone(status)
        
        # 获取账户信息
        account_info = execution_manager.get_account_info()
        self.assertIsInstance(account_info, dict)
        
        # 获取持仓
        positions = execution_manager.get_current_positions()
        self.assertIsInstance(positions, list)


class IntegrationTest(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        # 创建测试数据
        dates = pd.date_range(start='2023-01-01', periods=60, freq='D')
        np.random.seed(42)
        prices = 10 + np.cumsum(np.random.randn(60) * 0.1)
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000000, 2000000, 60),
            'amount': prices * np.random.randint(1000000, 2000000, 60)
        })
    
    def test_end_to_end_workflow(self):
        """端到端工作流程测试"""
        # 1. 创建策略
        config = {
            "name": "IntegrationTest",
            "window": 5,
            "threshold": 0.02,
            "initial_cash": 50000
        }
        strategy = MomentumStrategy(config)
        
        # 2. 运行回测
        backtest_engine = AdvancedBacktestEngine(initial_cash=50000)
        backtest_result, metrics = backtest_engine.run_backtest(self.test_data, strategy)
        
        # 3. 验证回测结果
        self.assertIsInstance(backtest_result, pd.DataFrame)
        self.assertGreaterEqual(len(backtest_result), 10)  # 至少有一些数据点
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_return', metrics)
        
        # 4. 风险管理
        risk_manager = RiskManager(max_drawdown=0.1)
        risk_manager.set_initial_capital(50000)
        risk_manager.update_portfolio_value(backtest_result['total_value'].iloc[-1])
        
        risk_check, risk_msg = risk_manager.check_risk_limits()
        self.assertIsInstance(risk_check, bool)
        
        # 5. 模拟交易执行
        broker = PaperTradingBroker(initial_balance=50000)
        execution_manager = ExecutionManager(broker)
        
        # 执行一个简单的交易
        order_id = execution_manager.execute_order(
            "000001.SZ", OrderSide.BUY, 100, OrderType.MARKET
        )
        
        self.assertIsNotNone(order_id)
        
        # 验证最终状态
        final_account_info = execution_manager.get_account_info()
        self.assertIsInstance(final_account_info, dict)
        self.assertIn('available_funds', final_account_info)


if __name__ == '__main__':
    print("运行量化交易系统测试...")
    
    # 运行所有测试
    unittest.main(verbosity=2)
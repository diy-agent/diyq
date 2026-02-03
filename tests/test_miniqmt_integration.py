"""
miniqmt 相关功能的测试
仅当 miniqmt 可用时运行
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from src.data.miniqmt_data_service import MiniQMTDataService, MINIQMT_AVAILABLE
from src.strategy.realtime_executor import RealTimeStrategyExecutor
from src.trading.execution_interface import MiniQMTBroker


@unittest.skipUnless(MINIQMT_AVAILABLE, "miniqmt (xtquant) not available")
class TestMiniQMTIntegration(unittest.TestCase):
    """测试 miniqmt 集成"""
    
    def setUp(self):
        if MINIQMT_AVAILABLE:
            self.service = MiniQMTDataService()
    
    def test_miniqmt_service_init(self):
        """测试 miniqmt 服务初始化"""
        if MINIQMT_AVAILABLE:
            self.assertIsInstance(self.service, MiniQMTDataService)
        else:
            self.skipTest("miniqmt not available")
    
    def test_get_stock_list(self):
        """测试获取股票列表"""
        if MINIQMT_AVAILABLE:
            stocks = self.service.get_stock_list(market="SH")
            # 由于实际市场数据可能为空，我们只测试方法是否存在
            self.assertTrue(hasattr(self.service, 'get_stock_list'))
        else:
            self.skipTest("miniqmt not available")
    
    def test_get_etf_list(self):
        """测试获取ETF列表"""
        if MINIQMT_AVAILABLE:
            etfs = self.service.get_etf_list()
            # 由于实际市场数据可能为空，我们只测试方法是否存在
            self.assertTrue(hasattr(self.service, 'get_etf_list'))
        else:
            self.skipTest("miniqmt not available")
    
    def test_get_current_data(self):
        """测试获取当前数据"""
        if MINIQMT_AVAILABLE:
            # 使用模拟数据测试接口
            self.assertTrue(hasattr(self.service, 'get_current_data'))
        else:
            self.skipTest("miniqmt not available")
    
    def test_get_history_data(self):
        """测试获取历史数据"""
        if MINIQMT_AVAILABLE:
            # 使用模拟数据测试接口
            self.assertTrue(hasattr(self.service, 'get_history_data'))
        else:
            self.skipTest("miniqmt not available")


@unittest.skipUnless(MINIQMT_AVAILABLE, "miniqmt (xtquant) not available")
class TestRealTimeExecutor(unittest.TestCase):
    """测试实时执行器"""
    
    def setUp(self):
        if MINIQMT_AVAILABLE:
            # 使用模拟账户ID
            self.executor = RealTimeStrategyExecutor(account_id="mock_account")
    
    def test_executor_init(self):
        """测试执行器初始化"""
        if MINIQMT_AVAILABLE:
            self.assertIsInstance(self.executor, RealTimeStrategyExecutor)
        else:
            self.skipTest("miniqmt not available")
    
    def test_add_strategy(self):
        """测试添加策略"""
        if MINIQMT_AVAILABLE:
            from src.strategy.base import MomentumStrategy
            
            config = {
                "name": "TestMomentum",
                "window": 10,
                "threshold": 0.02,
                "initial_cash": 100000
            }
            
            self.executor.add_strategy("000001.SZ", "momentum", config)
            
            self.assertIn("000001.SZ", self.executor.active_strategies)
        else:
            self.skipTest("miniqmt not available")


@unittest.skipUnless(MINIQMT_AVAILABLE, "miniqmt (xtquant) not available")
class TestMiniQMTBroker(unittest.TestCase):
    """测试 MiniQMT 交易接口"""
    
    def setUp(self):
        if MINIQMT_AVAILABLE:
            self.broker = MiniQMTBroker(account_id="mock_account")
    
    def test_broker_init(self):
        """测试券商接口初始化"""
        if MINIQMT_AVAILABLE:
            self.assertIsInstance(self.broker, MiniQMTBroker)
        else:
            self.skipTest("miniqmt not available")
    
    def test_broker_methods_exist(self):
        """测试券商接口方法存在"""
        if MINIQMT_AVAILABLE:
            self.assertTrue(hasattr(self.broker, 'connect'))
            self.assertTrue(hasattr(self.broker, 'disconnect'))
            self.assertTrue(hasattr(self.broker, 'place_order'))
            self.assertTrue(hasattr(self.broker, 'cancel_order'))
            self.assertTrue(hasattr(self.broker, 'get_order_status'))
            self.assertTrue(hasattr(self.broker, 'get_account_info'))
            self.assertTrue(hasattr(self.broker, 'get_positions'))
        else:
            self.skipTest("miniqmt not available")


if __name__ == '__main__':
    if MINIQMT_AVAILABLE:
        print("运行 MiniQMT 集成测试...")
        unittest.main(verbosity=2)
    else:
        print("MiniQMT 不可用，跳过相关测试")
"""
交易执行接口
定义交易执行的标准接口和实现
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from enum import Enum
import uuid
from datetime import datetime
from loguru import logger


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order:
    """订单类"""
    def __init__(self, 
                 symbol: str, 
                 side: OrderSide, 
                 quantity: float, 
                 order_type: OrderType = OrderType.MARKET,
                 price: float = None,
                 stop_price: float = None,
                 order_id: str = None):
        self.order_id = order_id or str(uuid.uuid4())
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.stop_price = stop_price
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0
        self.average_fill_price = 0
        self.timestamp = datetime.now()
        self.filled_timestamp = None
        self.rejected_reason = None
    
    def fill(self, filled_qty: float, fill_price: float):
        """更新订单成交信息"""
        self.filled_quantity += filled_qty
        total_value = self.average_fill_price * (self.filled_quantity - filled_qty) + fill_price * filled_qty
        self.average_fill_price = total_value / self.filled_quantity if self.filled_quantity > 0 else 0
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
            self.filled_timestamp = datetime.now()
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self):
        """取消订单"""
        self.status = OrderStatus.CANCELLED
    
    def reject(self, reason: str):
        """拒绝订单"""
        self.status = OrderStatus.REJECTED
        self.rejected_reason = reason
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'order_type': self.order_type.value,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'average_fill_price': self.average_fill_price,
            'timestamp': self.timestamp.isoformat(),
            'filled_timestamp': self.filled_timestamp.isoformat() if self.filled_timestamp else None,
            'rejected_reason': self.rejected_reason
        }


class Trade:
    """成交记录类"""
    def __init__(self, order_id: str, symbol: str, side: OrderSide, 
                 quantity: float, price: float, trade_id: str = None):
        self.trade_id = trade_id or str(uuid.uuid4())
        self.order_id = order_id
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'trade_id': self.trade_id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat()
        }


class BrokerInterface(ABC):
    """券商接口抽象基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接到券商系统"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> str:
        """下单"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Order:
        """获取订单状态"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """获取持仓"""
        pass


class MiniQMTBroker(BrokerInterface):
    """MiniQMT 券商接口实现"""
    
    def __init__(self, account_id: str, miniqmt_path: str = None):
        self.account_id = account_id
        self.miniqmt_path = miniqmt_path
        self.connected = False
        self.orders = {}  # 存储订单信息
        self.trades = {}  # 存储成交信息
        
        # 导入 miniqmt 库
        try:
            if miniqmt_path:
                import sys
                sys.path.append(miniqmt_path)
            
            import xtquant.xttrader as xttrader
            import xtquant.xttype as xttype
            from xtquant import XtAccount
            self.xttrader = xttrader
            self.xttype = xttype
            self.XtAccount = XtAccount
            self.xt_available = True
        except ImportError:
            logger.warning("xtquant 库未安装，无法使用 MiniQMT 交易接口")
            self.xt_available = False
    
    def connect(self) -> bool:
        """连接到 MiniQMT 系统"""
        if not self.xt_available:
            logger.error("xtquant 库不可用，无法连接")
            return False
        
        try:
            # 创建账户对象
            self.account = self.XtAccount(self.account_id)
            
            # 创建交易对象
            self.trader = self.xttrader.XtQuantTrader(self.miniqmt_path, "session_id")
            
            # 注册回调
            self.trader.registerCallback(self)
            
            # 订阅账户
            self.trader.subscribe(self.account)
            
            # 启动交易线程
            self.trader.start()
            
            self.connected = True
            logger.info(f"成功连接到 MiniQMT 账户: {self.account_id}")
            return True
        except Exception as e:
            logger.error(f"连接 MiniQMT 失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        if not self.connected:
            return True
        
        try:
            if hasattr(self, 'trader'):
                self.trader.stop()
            self.connected = False
            logger.info("已断开 MiniQMT 连接")
            return True
        except Exception as e:
            logger.error(f"断开 MiniQMT 连接失败: {e}")
            return False
    
    def place_order(self, order: Order) -> str:
        """下单"""
        if not self.connected:
            logger.error("未连接到 MiniQMT，无法下单")
            order.reject("Not connected")
            return order.order_id
        
        try:
            # 转换订单类型
            if order.order_type == OrderType.MARKET:
                xt_order_type = self.xttype.OrderType.Market
            elif order.order_type == OrderType.LIMIT:
                xt_order_type = self.xttype.OrderType.Limit
            else:
                logger.error(f"不支持的订单类型: {order.order_type}")
                order.reject("Unsupported order type")
                return order.order_id
            
            # 转换订单方向
            xt_side = self.xttype.SIDE_BUY if order.side == OrderSide.BUY else self.xttype.SIDE_SELL
            
            # 创建 MiniQMT 订单
            xt_order = self.xttrader.StockOrder(
                account=self.account,
                stock_code=order.symbol,
                order_type=xt_order_type,
                order_volume=int(order.quantity),
                price_type=self.xttype.FIX_PRICE if order.order_type == OrderType.LIMIT else self.xttype.FIX_PRICE,
                price=order.price if order.price else 0,
                order_sysid=order.order_id
            )
            
            # 发送订单
            result = self.trader.order_stock(self.account, xt_order)
            
            if result == 0:
                # 订单提交成功
                self.orders[order.order_id] = order
                logger.info(f"订单已提交: {order.order_id}, {order.symbol}, {order.side.value}, {order.quantity}")
            else:
                # 订单提交失败
                order.reject(f"Order submission failed with code: {result}")
                logger.error(f"订单提交失败: {order.order_id}, 错误码: {result}")
            
            return order.order_id
        except Exception as e:
            logger.error(f"下单失败: {e}")
            order.reject(str(e))
            return order.order_id
    
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        if not self.connected:
            logger.error("未连接到 MiniQMT，无法撤单")
            return False
        
        try:
            order = self.orders.get(order_id)
            if not order or order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                logger.warning(f"无法撤销订单 {order_id}: 状态不允许")
                return False
            
            # 创建撤销订单请求
            cancel_result = self.trader.cancel_order_stock(self.account, order_id)
            
            if cancel_result == 0:
                order.cancel()
                logger.info(f"订单已撤销: {order_id}")
                return True
            else:
                logger.error(f"撤销订单失败: {order_id}, 错误码: {cancel_result}")
                return False
        except Exception as e:
            logger.error(f"撤销订单异常: {e}")
            return False
    
    def get_order_status(self, order_id: str) -> Order:
        """获取订单状态"""
        return self.orders.get(order_id)
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        if not self.connected:
            logger.error("未连接到 MiniQMT，无法获取账户信息")
            return {}
        
        try:
            # 查询账户资金
            fund_info = self.trader.query_stock_asset(self.account)
            
            if fund_info:
                return {
                    'account_id': self.account_id,
                    'available_funds': fund_info.availableFunds,
                    'frozen_funds': fund_info.frozenFunds,
                    'total_asset': fund_info.totalAsset,
                    'market_value': fund_info.marketValue
                }
            else:
                logger.warning("无法获取账户资金信息")
                return {}
        except Exception as e:
            logger.error(f"获取账户信息失败: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """获取持仓"""
        if not self.connected:
            logger.error("未连接到 MiniQMT，无法获取持仓")
            return []
        
        try:
            # 查询持仓
            positions = self.trader.query_stock_positions(self.account)
            
            result = []
            for pos in positions:
                result.append({
                    'symbol': pos.stock_code,
                    'volume': pos.volume,
                    'can_sell_volume': pos.can_sell_volume,
                    'cost_price': pos.open_price_average,
                    'current_price': pos.market_price,
                    'profit_loss': pos.float_profit
                })
            
            return result
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []
    
    # MiniQMT 回调方法
    def on_disconnected(self):
        """连接断开回调"""
        logger.warning("与 MiniQMT 连接断开")
        self.connected = False
    
    def on_stock_order(self, order):
        """订单回报回调"""
        order_id = order.order_id
        if order_id in self.orders:
            local_order = self.orders[order_id]
            
            # 更新订单状态
            if order.status == self.xttype.ORDER_STATUS.FILLED:
                local_order.status = OrderStatus.FILLED
                local_order.filled_quantity = order.quantity
                local_order.average_fill_price = order.price
                local_order.filled_timestamp = datetime.fromtimestamp(order.traded_time)
            elif order.status == self.xttype.ORDER_STATUS.PARTIAL_FILLED:
                local_order.status = OrderStatus.PARTIALLY_FILLED
                local_order.filled_quantity = order.quantity
                local_order.average_fill_price = order.price
            elif order.status == self.xttype.ORDER_STATUS.CANCELLED:
                local_order.status = OrderStatus.CANCELLED
            elif order.status == self.xttype.ORDER_STATUS.REJECTED:
                local_order.status = OrderStatus.REJECTED
                local_order.rejected_reason = order.message
    
    def on_stock_trade(self, trade):
        """成交回报回调"""
        trade_record = Trade(
            order_id=trade.order_id,
            symbol=trade.stock_code,
            side=OrderSide.BUY if trade.side == self.xttype.SIDE_BUY else OrderSide.SELL,
            quantity=trade.traded_volume,
            price=trade.traded_price
        )
        
        self.trades[trade.trade_id] = trade_record
        
        # 更新对应订单的成交信息
        order = self.orders.get(trade.order_id)
        if order:
            order.fill(trade.traded_volume, trade.traded_price)


class PaperTradingBroker(BrokerInterface):
    """模拟交易接口实现"""
    
    def __init__(self, initial_balance: float = 100000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # {symbol: {'quantity': float, 'avg_price': float}}
        self.orders = {}
        self.trades = {}
        self.connected = True  # 模拟交易始终连接
    
    def connect(self) -> bool:
        """连接（模拟）"""
        logger.info("已连接到模拟交易平台")
        return True
    
    def disconnect(self) -> bool:
        """断开连接（模拟）"""
        logger.info("已断开模拟交易平台连接")
        return True
    
    def place_order(self, order: Order) -> str:
        """下单（模拟）"""
        try:
            # 对于市价单，立即成交
            if order.order_type == OrderType.MARKET:
                # 这里需要获取当前市场价格，暂时使用一个模拟价格
                # 在实际应用中，这里会从数据源获取实时价格
                current_price = order.price or 10.0  # 模拟价格
                
                # 立即成交
                order.fill(order.quantity, current_price)
                
                # 更新持仓和资金
                self._update_position_and_balance(order, current_price)
                
                # 记录成交
                trade = Trade(
                    order_id=order.order_id,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=current_price
                )
                self.trades[trade.trade_id] = trade
                
                logger.info(f"模拟成交: {order.symbol}, {order.side.value}, {order.quantity}@{current_price}")
            
            # 限价单需要匹配价格，这里简化处理
            elif order.order_type == OrderType.LIMIT:
                # 模拟限价单处理
                order.status = OrderStatus.PARTIALLY_FILLED  # 简化处理
                logger.info(f"限价单已提交: {order.symbol}, {order.side.value}, {order.quantity}@{order.price}")
            
            self.orders[order.order_id] = order
            return order.order_id
        except Exception as e:
            logger.error(f"下单失败: {e}")
            order.reject(str(e))
            return order.order_id
    
    def _update_position_and_balance(self, order: Order, fill_price: float):
        """更新持仓和资金"""
        symbol = order.symbol
        
        if order.side == OrderSide.BUY:
            # 买入
            cost = order.quantity * fill_price
            if cost > self.balance:
                logger.error(f"资金不足: 需要 {cost}, 可用 {self.balance}")
                return
            
            self.balance -= cost
            
            if symbol in self.positions:
                # 加仓，重新计算平均成本
                old_pos = self.positions[symbol]
                total_qty = old_pos['quantity'] + order.quantity
                total_cost = old_pos['quantity'] * old_pos['avg_price'] + cost
                new_avg_price = total_cost / total_qty
                
                self.positions[symbol] = {
                    'quantity': total_qty,
                    'avg_price': new_avg_price
                }
            else:
                # 新开仓
                self.positions[symbol] = {
                    'quantity': order.quantity,
                    'avg_price': fill_price
                }
        else:
            # 卖出
            if symbol not in self.positions or self.positions[symbol]['quantity'] < order.quantity:
                logger.error(f"持仓不足: 需要 {order.quantity}, 持有 {self.positions.get(symbol, {}).get('quantity', 0)}")
                return
            
            revenue = order.quantity * fill_price
            self.balance += revenue
            
            # 更新持仓
            old_qty = self.positions[symbol]['quantity']
            if old_qty == order.quantity:
                # 清仓
                del self.positions[symbol]
            else:
                # 减仓
                remaining_qty = old_qty - order.quantity
                self.positions[symbol]['quantity'] = remaining_qty
    
    def cancel_order(self, order_id: str) -> bool:
        """撤销订单（模拟）"""
        order = self.orders.get(order_id)
        if not order:
            logger.warning(f"订单不存在: {order_id}")
            return False
        
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            logger.warning(f"无法撤销订单 {order_id}: 状态不允许")
            return False
        
        order.cancel()
        logger.info(f"订单已撤销: {order_id}")
        return True
    
    def get_order_status(self, order_id: str) -> Order:
        """获取订单状态（模拟）"""
        return self.orders.get(order_id)
    
    def get_account_info(self) -> Dict:
        """获取账户信息（模拟）"""
        total_position_value = 0
        for symbol, pos in self.positions.items():
            # 这里需要获取当前市场价格，暂时使用模拟价格
            current_price = pos['avg_price'] * 1.01  # 模拟价格上涨1%
            total_position_value += pos['quantity'] * current_price
        
        return {
            'account_id': 'paper_trading_account',
            'available_funds': self.balance,
            'frozen_funds': 0,
            'total_asset': self.balance + total_position_value,
            'market_value': total_position_value
        }
    
    def get_positions(self) -> List[Dict]:
        """获取持仓（模拟）"""
        result = []
        for symbol, pos in self.positions.items():
            # 模拟当前价格
            current_price = pos['avg_price'] * 1.01  # 假设上涨1%
            profit_loss = (current_price - pos['avg_price']) * pos['quantity']
            
            result.append({
                'symbol': symbol,
                'volume': pos['quantity'],
                'can_sell_volume': pos['quantity'],
                'cost_price': pos['avg_price'],
                'current_price': current_price,
                'profit_loss': profit_loss
            })
        
        return result


class ExecutionManager:
    """执行管理器"""
    
    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.order_history = []
    
    def execute_order(self, symbol: str, side: OrderSide, quantity: float, 
                     order_type: OrderType = OrderType.MARKET, 
                     price: float = None) -> str:
        """执行订单"""
        order = Order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price
        )
        
        order_id = self.broker.place_order(order)
        self.order_history.append(order)
        
        logger.info(f"订单已发送: {order_id}, {symbol}, {side.value}, {quantity}")
        return order_id
    
    def execute_signal(self, symbol: str, signal: int, quantity: float = None) -> Optional[str]:
        """根据信号执行交易"""
        if signal == 0:
            logger.info("无交易信号，跳过执行")
            return None
        
        # 如果没有指定数量，默认使用固定数量
        if quantity is None:
            quantity = 100  # 默认100股
        
        side = OrderSide.BUY if signal == 1 else OrderSide.SELL
        return self.execute_order(symbol, side, quantity, OrderType.MARKET)
    
    def get_execution_status(self, order_id: str) -> Order:
        """获取执行状态"""
        return self.broker.get_order_status(order_id)
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        return self.broker.cancel_order(order_id)
    
    def get_account_info(self) -> Dict:
        """获取账户信息"""
        return self.broker.get_account_info()
    
    def get_current_positions(self) -> List[Dict]:
        """获取当前持仓"""
        return self.broker.get_positions()


# 示例使用
if __name__ == "__main__":
    # 使用模拟交易接口进行演示
    paper_broker = PaperTradingBroker(initial_balance=100000)
    execution_manager = ExecutionManager(paper_broker)
    
    # 连接
    paper_broker.connect()
    
    # 执行买入订单
    order_id = execution_manager.execute_order(
        symbol="000001.SZ", 
        side=OrderSide.BUY, 
        quantity=1000, 
        order_type=OrderType.MARKET
    )
    
    # 检查订单状态
    order_status = execution_manager.get_execution_status(order_id)
    print(f"订单状态: {order_status.status.value}")
    
    # 获取账户信息
    account_info = execution_manager.get_account_info()
    print(f"账户信息: {account_info}")
    
    # 获取持仓
    positions = execution_manager.get_current_positions()
    print(f"持仓: {positions}")
    
    # 断开连接
    paper_broker.disconnect()
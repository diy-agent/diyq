 eee# 量化交易系统开发指南

本文档介绍如何开发和扩展基于 miniqmt 的量化交易系统。

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   数据层        │────│   策略层         │────│   交易执行层     │
│                 │    │                  │    │                 │
│ • 数据获取      │    │ • 策略基类       │    │ • 交易接口       │
│ • 数据预处理    │    │ • 具体策略实现   │    │ • 订单管理       │
│ • 数据存储      │    │ • 信号生成       │    │ • 执行管理       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   回测层        │    │   风险管理层      │    │   应用层        │
│                 │    │                  │    │                 │
│ • 回测引擎      │    │ • 仓位管理       │    │ • Web UI       │
│ • 指标计算      │    │ • 风险控制       │    │ • 配置管理      │
│ • 结果分析      │    │ • 资金管理       │    │ • 日志记录      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 核心模块开发

### 1. 数据模块开发

数据模块负责市场数据的获取、处理和存储。

#### 扩展数据源

```python
# 在 src/data/ 中创建新的数据服务
from abc import ABC, abstractmethod
import pandas as pd

class DataSource(ABC):
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_realtime_data(self, symbol: str) -> dict:
        pass

class NewDataSource(DataSource):
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # 实现数据获取逻辑
        pass
    
    def get_realtime_data(self, symbol: str) -> dict:
        # 实现实时数据获取逻辑
        pass
```

#### 数据标准化

所有数据源应返回标准化的数据格式：

```python
# 标准化列名
required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
```

### 2. 策略模块开发

策略模块是系统的核心，包含策略逻辑和信号生成。

#### 创建新策略

继承 `BaseStrategy` 类创建新策略：

```python
from src.strategy.base import BaseStrategy
import pandas as pd

class MyNewStrategy(BaseStrategy):
    def __init__(self, config: dict):
        super().__init__(config)
        # 初始化策略参数
        self.param1 = config.get("param1", 10)
        self.param2 = config.get("param2", 20)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        返回包含 'signal' 列的 DataFrame
        signal: 1=买入, -1=卖出, 0=持有
        """
        df = df.copy()
        
        # 实现策略逻辑
        # ...
        
        # 生成信号
        df['signal'] = 0  # 默认持有
        df.loc[condition1, 'signal'] = 1   # 买入信号
        df.loc[condition2, 'signal'] = -1  # 卖出信号
        
        return df
```

#### 策略注册

在策略管理器中注册新策略：

```python
from src.strategy.base import StrategyManager

manager = StrategyManager()
manager.register_strategy("my_new_strategy", MyNewStrategy)
```

### 3. 回测引擎开发

回测引擎评估策略表现。

#### 自定义回测指标

```python
from src.strategy.backtest_engine import AdvancedBacktestEngine

class CustomBacktestEngine(AdvancedBacktestEngine):
    def _calculate_custom_metrics(self, df: pd.DataFrame) -> dict:
        """计算自定义指标"""
        # 实现自定义指标计算逻辑
        custom_metric = df['some_calculation'].mean()
        return {'custom_metric': custom_metric}
    
    def run_backtest(self, data: pd.DataFrame, strategy, **kwargs):
        # 调用父类方法
        results, metrics = super().run_backtest(data, strategy, **kwargs)
        
        # 添加自定义指标
        custom_metrics = self._calculate_custom_metrics(results)
        metrics.update(custom_metrics)
        
        return results, metrics
```

### 4. 风险管理开发

风险管理模块保护资本和控制风险。

#### 自定义风险规则

```python
from src.utils.risk_manager import RiskManager

class EnhancedRiskManager(RiskManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correlation_limit = kwargs.get('correlation_limit', 0.7)
    
    def check_correlation_risk(self, new_position_symbol: str) -> tuple[bool, str]:
        """检查相关性风险"""
        # 实现相关性风险检查逻辑
        for existing_symbol in self.positions:
            correlation = self._calculate_correlation(new_position_symbol, existing_symbol)
            if correlation > self.correlation_limit:
                return False, f"与 {existing_symbol} 相关性过高: {correlation:.2f}"
        return True, "相关性风险检查通过"
    
    def check_risk_limits(self, symbol: str = None) -> tuple[bool, str]:
        """重写风险检查方法，加入相关性检查"""
        # 先运行原有检查
        ok, msg = super().check_risk_limits(symbol)
        if not ok:
            return ok, msg
        
        # 添加相关性检查
        if symbol:
            return self.check_correlation_risk(symbol)
        
        return True, "所有风险检查通过"
```

### 5. 交易执行开发

交易执行模块处理订单和执行。

#### 新增交易接口

```python
from src.trading.execution_interface import BrokerInterface, Order

class NewBrokerInterface(BrokerInterface):
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = None
    
    def connect(self) -> bool:
        # 实现连接逻辑
        pass
    
    def disconnect(self) -> bool:
        # 实现断开连接逻辑
        pass
    
    def place_order(self, order: Order) -> str:
        # 实现下单逻辑
        pass
    
    def cancel_order(self, order_id: str) -> bool:
        # 实现撤单逻辑
        pass
    
    def get_order_status(self, order_id: str) -> Order:
        # 实现查询订单状态逻辑
        pass
    
    def get_account_info(self) -> dict:
        # 实现查询账户信息逻辑
        pass
    
    def get_positions(self) -> list[dict]:
        # 实现查询持仓逻辑
        pass
```

## 最佳实践

### 1. 代码组织

- 每个模块职责单一
- 使用抽象基类定义接口
- 遵循 SOLID 原则
- 编写充分的单元测试

### 2. 错误处理

```python
from loguru import logger

def risky_operation(self):
    try:
        # 执行可能失败的操作
        result = some_operation()
        return result
    except SpecificException as e:
        logger.error(f"操作失败: {e}")
        # 实现降级逻辑
        return self.fallback_method()
    except Exception as e:
        logger.exception(f"未预期错误: {e}")
        # 重新抛出或处理
        raise
```

### 3. 性能优化

- 使用 Pandas 向量化操作
- 缓存频繁访问的数据
- 异步处理 I/O 操作
- 使用适当的数据结构

### 4. 配置管理

使用配置文件管理参数：

```python
# config.json
{
    "strategy_params": {
        "momentum": {
            "window": 20,
            "threshold": 0.05
        }
    },
    "risk_params": {
        "max_drawdown": 0.15,
        "stop_loss_pct": 0.08
    }
}
```

### 5. 日志记录

```python
from loguru import logger

logger.info(f"策略 {strategy.name} 生成信号: {signal}")
logger.warning(f"风险阈值接近: {risk_level}")
logger.error(f"订单执行失败: {order_id}")
```

## 扩展示例

### 自定义指标策略

```python
import talib
import numpy as np

class TechnicalIndicatorStrategy(BaseStrategy):
    def __init__(self, config: dict):
        super().__init__(config)
        self.rsi_period = config.get("rsi_period", 14)
        self.macd_fast = config.get("macd_fast", 12)
        self.macd_slow = config.get("macd_slow", 26)
        self.macd_signal = config.get("macd_signal", 9)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # 计算 RSI
        df['rsi'] = talib.RSI(df['close'].values, timeperiod=self.rsi_period)
        
        # 计算 MACD
        macd, macdsignal, macdhist = talib.MACD(
            df['close'].values,
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal
        )
        df['macd'] = macd
        df['macd_signal'] = macdsignal
        df['macd_hist'] = macdhist
        
        # 生成信号
        df['signal'] = 0
        # RSI 超卖买入
        df.loc[(df['rsi'] < 30) & (df['macd'] > df['macd_signal']), 'signal'] = 1
        # RSI 超买卖出
        df.loc[(df['rsi'] > 70) & (df['macd'] < df['macd_signal']), 'signal'] = -1
        
        return df
```

### 事件驱动策略

```python
from queue import Queue
import threading

class EventDrivenStrategy(BaseStrategy):
    def __init__(self, config: dict):
        super().__init__(config)
        self.event_queue = Queue()
        self.event_thread = None
        self.running = False
    
    def start_event_processing(self):
        """启动事件处理线程"""
        self.running = True
        self.event_thread = threading.Thread(target=self._process_events)
        self.event_thread.start()
    
    def stop_event_processing(self):
        """停止事件处理"""
        self.running = False
        if self.event_thread:
            self.event_thread.join()
    
    def _process_events(self):
        """处理事件队列"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                signal = self._generate_signal_from_event(event)
                # 执行交易
                self._execute_signal(signal)
            except:
                continue  # 队列为空时继续循环
    
    def _generate_signal_from_event(self, event) -> int:
        """从事件生成信号"""
        # 实现事件到信号的转换逻辑
        pass
    
    def _execute_signal(self, signal: int):
        """执行信号"""
        # 实现信号执行逻辑
        pass
```

## 调试和监控

### 调试技巧

1. 使用日志记录中间结果
2. 实现策略的逐步执行模式
3. 使用断点调试复杂逻辑
4. 记录和分析交易决策过程

### 监控指标

- 策略收益率和风险指标
- 订单成功率和执行质量
- 系统资源使用情况
- 数据质量和延迟

## 部署考虑

### 生产环境配置

- 使用配置文件管理环境变量
- 设置适当的日志级别
- 实现健康检查端点
- 配置备份和恢复机制

### 安全考虑

- 保护 API 密钥和账户信息
- 实现访问控制和认证
- 加密敏感数据传输
- 定期安全审计

通过遵循这些指南，您可以有效地扩展和定制量化交易系统以满足特定需求。
# 基于 miniqmt 的量化交易系统

这是一个基于 miniqmt（xtquant）的量化交易系统，集成了数据获取、策略开发、回测、风险管理和实盘交易功能。

## 项目结构

```
_quant/
├── main.py                 # 主入口文件
├── pyproject.toml          # 项目依赖配置
├── README.md              # 项目说明
├── configs/               # 配置文件
├── data/                  # 数据存储
├── docs/                  # 文档
├── src/                   # 源代码
│   ├── data/              # 数据模块
│   │   ├── downloader.py     # 数据下载器
│   │   └── miniqmt_data_service.py  # miniqmt 数据服务
│   ├── strategy/          # 策略模块
│   │   ├── base.py           # 策略基类和基础策略
│   │   ├── realtime_executor.py  # 实时策略执行器
│   │   └── backtest_engine.py    # 回测引擎
│   ├── trading/           # 交易模块
│   │   └── execution_interface.py  # 交易执行接口
│   ├── ui/                # 用户界面
│   │   └── app.py            # Streamlit 应用
│   └── utils/             # 工具模块
│       ├── config_manager.py # 配置管理
│       └── risk_manager.py   # 风险管理
├── tests/                 # 测试用例
└── ref/                   # 参考资料
```

## 安装和配置

### 1. 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd _quant

# 使用 uv 管理依赖（推荐）
uv venv  # 创建虚拟环境
source .venv/bin/activate  # 激活虚拟环境
uv sync  # 安装依赖
```

### 2. miniqmt 配置

要使用 miniqmt 功能，需要：

1. 联系券商开通 miniqmt 权限
2. 下载对应的 xtquant 库
3. 将其安装到 Python 环境中

```python
# 通常需要从券商获取安装包
# pip install <xtquant_package_from_broker>.whl
```

## 核心功能

### 1. 数据获取

系统支持多种数据源：

- **AKShare**: 作为备用数据源
- **miniqmt**: 实时和历史数据获取

```python
from src.data.downloader import DataDownloader

downloader = DataDownloader()
etf_list = downloader.get_etf_list()
data = downloader.download_kline("510300")
```

### 2. 策略框架

系统提供多种策略模板：

- **动量策略**: 基于价格动量的策略
- **均值回归策略**: 基于价格回归均值的策略
- **移动平均线交叉策略**: 基于均线交叉的策略

```python
from src.strategy.base import MomentumStrategy

config = {
    "name": "MyMomentumStrategy",
    "window": 20,
    "threshold": 0.05,
    "initial_cash": 100000
}

strategy = MomentumStrategy(config)
```

### 3. 回测引擎

提供基础和高级回测功能：

```python
from src.strategy.backtest_engine import AdvancedBacktestEngine

engine = AdvancedBacktestEngine(initial_cash=100000)
results, metrics = engine.run_backtest(historical_data, strategy)
```

### 4. 风险管理

集成多种风险管理工具：

- **VaR计算**: 风险价值评估
- **组合优化**: 资产配置优化
- **止损止盈**: 自动风险控制

```python
from src.utils.risk_manager import RiskManager

risk_manager = RiskManager(
    max_portfolio_risk=0.02,
    max_position_risk=0.01,
    max_drawdown=0.15,
    stop_loss_pct=0.08
)
```

### 5. 交易执行

支持模拟交易和实盘交易：

```python
from src.trading.execution_interface import PaperTradingBroker, ExecutionManager

broker = PaperTradingBroker(initial_balance=100000)
executor = ExecutionManager(broker)

# 执行订单
order_id = executor.execute_order("000001.SZ", OrderSide.BUY, 1000)
```

## 使用示例

### 1. 简单回测示例

```python
import pandas as pd
from src.data.downloader import DataDownloader
from src.strategy.base import MomentumStrategy
from src.strategy.backtest_engine import AdvancedBacktestEngine

# 获取数据
downloader = DataDownloader()
data = downloader.download_kline("510300", start_date="2023-01-01")

# 创建策略
strategy_config = {
    "name": "ExampleMomentum",
    "window": 10,
    "threshold": 0.03,
    "initial_cash": 100000
}
strategy = MomentumStrategy(strategy_config)

# 运行回测
engine = AdvancedBacktestEngine(initial_cash=100000)
results, metrics = engine.run_backtest(data, strategy)

print(f"总收益率: {metrics['total_return']:.2%}")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {metrics['max_drawdown']:.2%}")
```

### 2. 实时策略执行（需要 miniqmt）

```python
from src.strategy.realtime_executor import RealTimeStrategyExecutor

# 创建实时执行器
executor = RealTimeStrategyExecutor(account_id="your_account_id")

# 添加策略
momentum_config = {
    "name": "RealTimeMomentum",
    "window": 10,
    "threshold": 0.03,
    "initial_cash": 50000
}
executor.add_strategy("000001.SZ", "momentum", momentum_config)

# 启动执行器
executor.start()

# 运行一段时间后停止
import time
time.sleep(300)  # 运行5分钟
executor.stop()
```

### 3. 多策略比较

```python
from src.strategy.backtest_engine import MultiStrategyBacktester
from src.strategy.base import MomentumStrategy, MeanReversionStrategy

# 创建多策略回测器
backtester = MultiStrategyBacktester(initial_cash=100000)

# 添加不同策略
momentum_strategy = MomentumStrategy({
    "name": "Momentum",
    "window": 10,
    "threshold": 0.03,
    "initial_cash": 100000
})

mean_rev_strategy = MeanReversionStrategy({
    "name": "MeanReversion",
    "window": 20,
    "std_multiplier": 2.0,
    "initial_cash": 100000
})

backtester.add_strategy("momentum", momentum_strategy)
backtester.add_strategy("mean_reversion", mean_rev_strategy)

# 运行回测
results = backtester.run_all(data)

# 比较结果
comparison = backtester.compare_results()
print(comparison)
```

## 配置管理

系统支持策略配置的保存和加载：

```python
from src.utils.config_manager import ConfigManager

config_manager = ConfigManager()

# 保存配置
config_manager.save_config("my_strategy", {
    "window": 20,
    "threshold": 0.05,
    "stop_loss": 0.08
})

# 加载配置
loaded_config = config_manager.load_config("my_strategy")
```

## UI 界面

系统包含 Streamlit 驱动的 Web 界面：

```bash
# 启动 UI
streamlit run src/ui/app.py
```

UI 界面提供：
- 策略参数配置
- 数据下载管理
- 回测结果展示
- 实时信号监控

## 测试

运行测试套件：

```bash
python -m pytest tests/ -v
```

## 注意事项

1. **实盘交易风险**: 本系统仅供学习和模拟使用，实盘交易需谨慎
2. **miniqmt依赖**: 实盘功能需要券商提供的 miniqmt 接口
3. **数据质量**: 确保使用高质量、准确的市场数据
4. **风险管理**: 始终实施适当的风险管理措施
5. **合规要求**: 遵守当地金融监管要求

## 扩展开发

系统设计为模块化，易于扩展：

- **新增策略**: 继承 `BaseStrategy` 类
- **新增数据源**: 实现相应的数据接口
- **新增风险模型**: 扩展 `RiskManager` 类
- **新增交易接口**: 实现 `BrokerInterface` 接口

## 许可证

[在此处添加许可证信息]
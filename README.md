# 基于 miniqmt 的量化交易系统

一个功能完整的量化交易系统，集成了数据获取、策略开发、回测、风险管理和实盘交易功能，特别针对 miniqmt（xtquant）进行了优化。

## 特性

- 📊 **多数据源支持**: 支持 AKShare 和 miniqmt 实时数据
- 🎯 **策略框架**: 灵活的策略开发和管理框架
- 📈 **回测引擎**: 完整的回测和绩效分析功能
- 🛡️ **风险管理**: 全面的风险控制和资金管理
- 💰 **交易执行**: 支持模拟和实盘交易
- 🖥️ **Web 界面**: Streamlit 驱动的用户界面
- 🧪 **测试覆盖**: 完整的单元测试和集成测试

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

### 环境准备

```bash
# 克隆项目
git clone <repository_url>
cd _quant

# 使用 uv 管理依赖（推荐）
uv venv  # 创建虚拟环境
source .venv/bin/activate  # 激活虚拟环境
uv sync  # 安装依赖
```

### miniqmt 配置

要使用 miniqmt 功能，需要：

1. 联系券商开通 miniqmt 权限
2. 下载对应的 xtquant 库
3. 将其安装到 Python 环境中

```python
# 通常需要从券商获取安装包
# pip install <xtquant_package_from_broker>.whl
```

## 快速开始

### 1. 运行 Web 界面

```bash
streamlit run src/ui/app.py
```

### 2. 简单回测示例

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

### 3. 运行测试

```bash
python -m pytest tests/ -v
```

## 核心功能

### 数据获取
- 支持 AKShare 作为备用数据源
- 集成 miniqmt 实时和历史数据获取
- 自动数据更新和缓存

### 策略框架
- 动量策略
- 均值回归策略
- 移动平均线交叉策略
- 易于扩展的策略基类

### 回测引擎
- 基础和高级回测功能
- 完整的绩效指标计算
- 多策略比较功能

### 风险管理
- VaR 和预期短缺计算
- 投资组合优化
- 止损止盈和风险限额

### 交易执行
- 模拟交易环境
- miniqmt 实盘交易接口
- 订单管理和执行跟踪

## 文档

- [用户指南](docs/user_guide.md) - 使用说明和示例
- [开发指南](docs/development_guide.md) - 扩展和定制开发

## 注意事项

1. **实盘交易风险**: 本系统仅供学习和模拟使用，实盘交易需谨慎
2. **miniqmt依赖**: 实盘功能需要券商提供的 miniqmt 接口
3. **数据质量**: 确保使用高质量、准确的市场数据
4. **风险管理**: 始终实施适当的风险管理措施
5. **合规要求**: 遵守当地金融监管要求

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

[在此处添加许可证信息]

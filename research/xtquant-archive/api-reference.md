# XTQuant API 参考文档

基于实际使用中整理的常用API接口。

## 核心模块: xtdata

```python
from xtquant import xtdata
```

## 1. 行情数据接口

### 1.1 获取最新行情

```python
quote = xtdata.get_latest_quote(["600000.SH", "000001.SZ"])
# 返回: dict, key为股票代码
# quote["600000.SH"]["lastPrice"]  # 最新价
```

### 1.2 获取K线数据

```python
# 方式1: get_market_data（基础版）
kline = xtdata.get_market_data(
    stock_list=["600000.SH"],     # 股票代码列表
    period="1d",                   # 周期: 1m/5m/15m/30m/60m/1d/1w/1M
    start_time="20260401",         # 开始时间 YYYYMMDD
    end_time="20260410",           # 结束时间 YYYYMMDD
    fields=["open", "high", "low", "close", "volume"]  # 可选字段
)
# 返回: dict {stock_code: DataFrame}

# 方式2: get_market_data_ex（扩展版，带时间戳）
raw_data = xtdata.get_market_data_ex(
    stock_list=["600519.SH"],
    period="1d",
    start_time="20240101",
    end_time="20240410"
)
# 返回: dict {stock_code: DataFrame}
# DataFrame包含 "time" 列（毫秒级时间戳）
```

### 1.3 下载历史数据

```python
xtdata.download_history_data2(
    stock_list=["600519.SH"],
    period="1d",
    start_time="20240101",
    end_time="20240410"
)
```

### 1.4 获取交易日历

```python
trade_dates = xtdata.get_trading_dates(
    market="SH",           # SH沪市 / SZ深市
    start_time="20260401",
    end_time="20260410"
)
# 返回: list[str], 例如 ['20260401', '20260402', ...]
```

## 2. 连接配置

### 2.1 自动连接（默认）

```python
from xtquant import xtdata
# 自动发现本地QMT服务，无需配置
```

### 2.2 自定义端口

```python
from xtquant import xtdata
xtdata.set_connect_port(58610)
```

### 2.3 自定义路径连接

```python
import sys
sys.path.insert(0, "D:/app/qmt/bin.x64")
from xtquant import xtdata
```

## 3. 数据周期说明

| 周期参数 | 说明 | 使用场景 |
|----------|------|----------|
| `1m` | 1分钟K线 | 日内超短线 |
| `5m` | 5分钟K线 | 日内短线 |
| `15m` | 15分钟K线 | 日内波段 |
| `30m` | 30分钟K线 | 日内趋势 |
| `60m` | 60分钟K线 | 日间过渡 |
| `1d` | 日K线 | 波段/趋势 |
| `1w` | 周K线 | 中长线 |
| `1M` | 月K线 | 长线 |

## 4. 股票代码格式

```
沪市: 代码.SH  例如 600519.SH (贵州茅台)
深市: 代码.SZ  例如 000001.SZ (平安银行)
创业板: 代码.SZ  例如 300750.SZ (宁德时代)
科创板: 代码.SH  例如 688981.SH (中芯国际)
ETF: 同股票代码格式  例如 510300.SH (沪深300ETF)
```

## 5. 数据处理示例

```python
import pandas as pd
from datetime import datetime
from xtquant import xtdata

# 获取K线数据
raw_data = xtdata.get_market_data_ex(
    stock_list=["600519.SH"],
    period="1d",
    start_time="20240101",
    end_time="20240410"
)

# 标准化处理
for stock_code, df in raw_data.items():
    df = df.reset_index()
    # 毫秒时间戳转为可读时间
    df["trade_time"] = df["time"].apply(
        lambda x: datetime.fromtimestamp(x/1000).strftime("%Y-%m-%d %H:%M:%S")
    )
    df = df.drop(columns=["time"])
    print(f"{stock_code}: {len(df)}条数据")
    print(df.head())
```

## 6. 完整测试脚本

```python
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, "d:/app/qmt/bin.x64")
sys.path.insert(0, "d:/app/qmt/python")

from xtquant import xtdata

print("开始xtquant接口测试...")

# 测试1: 获取最新行情
quote = xtdata.get_latest_quote(["600000.SH", "000001.SZ"])
if "600000.SH" in quote:
    print(f"1. 浦发银行(600000.SH)最新价: {quote['600000.SH']['lastPrice']}")

# 测试2: 获取K线数据
kline = xtdata.get_market_data(
    stock_list=["600000.SH"],
    period="1d",
    start_time="20260401",
    end_time="20260408",
    fields=["open", "high", "low", "close", "volume"],
)
if "600000.SH" in kline:
    df = kline["600000.SH"]
    print(f"2. 浦发银行近7日K线行数: {len(df)}")

# 测试3: 获取交易日历
trade_dates = xtdata.get_trading_dates(
    market="SH", start_time="20260401", end_time="20260410"
)
print(f"3. 交易日数量: {len(trade_dates)}")

print("xtquant接口全部测试通过")
```

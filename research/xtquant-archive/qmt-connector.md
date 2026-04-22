# QMT Connector 项目文档

从AI Agent聊天记录中恢复的完整项目：`~/.openclaw/workspace/qmt-connector/`

## 项目概述

QMT行情数据连接器，符合研究框架标准的可移植工具。

### 核心特性

| 模式 | 使用场景 | 配置要求 | 推荐指数 |
|------|----------|----------|----------|
| 🔥 自动连接模式（默认） | 本地运行官方QMT客户端 | 0配置，只要启动QMT就能用 | ⭐⭐⭐⭐⭐ |
| ⚙️ 自定义连接模式 | 多QMT实例并存、自定义端口 | 仅需指定QMT路径/端口 | ⭐⭐⭐ |

## 项目结构

```
qmt-connector/
├── config.toml                 # 可选配置文件
├── pyproject.toml             # uv项目配置
├── src/
│   └── qmt_connector/
│       ├── __init__.py
│       ├── config.py          # 配置加载模块
│       ├── data.py            # 核心数据模块
│       └── cli.py             # 命令行入口（Cyclopts）
└── data/                      # 数据默认保存目录
```

## 快速开始

### 1. 环境要求

- Python 3.10 ~ 3.12（QMT xtquant不支持3.13+）
- 已安装并启动QMT客户端
- 已安装uv: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

### 2. 安装

```bash
uv sync
```

### 3. 直接使用

```powershell
# 测试连接
uv run qmt test-connect

# 获取行情数据
uv run qmt get-data --stocks 600519.SH --start 20240101
```

## 配置文件

### config.toml

```toml
[qmt]
# QMT bin.x64目录路径，默认自动连接不需要修改
# bin_path = "D:\app\qmt\bin.x64"
# port = 58610
# auto_add_path = true

[output]
format = "json"
save_to_file = false
output_dir = "./data"
```

## 命令行用法

### 子命令列表

| 子命令 | 功能 |
|--------|------|
| `test-connect` | 测试QMT连接是否正常 |
| `get-data` | 获取行情数据 |
| `--help` | 查看帮助信息 |

### get-data 参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stocks` | `-s` | 必填，股票代码列表 | - |
| `--period` | `-p` | K线周期 | `1d` |
| `--start` | `-st` | 开始时间 `YYYYMMDD` | - |
| `--end` | `-e` | 结束时间 `YYYYMMDD` | 当前日期 |
| `--output` | `-o` | 输出文件路径 | - |
| `--format` | `-f` | 输出格式 `json/csv` | `json` |
| `--no-download` | - | 不下载历史数据 | `False` |

### 常用示例

```powershell
# 获取贵州茅台2024年1月1日至今的日K数据
uv run qmt get-data --stocks 600519.SH --start 20240101

# 获取多只股票的5分钟K线，保存为CSV
uv run qmt get-data --stocks 600519.SH 000001.SZ 002594.SZ \
    --period 5m --start 20240401 \
    --output ./stocks_5min.csv --format csv

# 直接输出JSON到控制台
uv run qmt get-data --stocks 600519.SH --start 20240101
```

## Python库使用

### 方式1: 默认自动连接（推荐）

```python
from qmt_connector.data import get_kline_data, save_data

# 自动连接本地QMT，不需要任何初始化代码
data = get_kline_data(
    stock_list=["600519.SH"],
    period="1d",
    start_time="20240101"
)
save_data(data, "maotai.json")
```

### 方式2: 自定义连接

```python
from qmt_connector.data import init_custom, get_kline_data

# 手动初始化自定义连接，只需调用一次
init_custom(
    bin_path="D:\app\qmt\bin.x64",
    port=58610  # 可选
)

# 后续使用和自动模式完全一致
data = get_kline_data(stock_list=["000001.SZ"], period="1d")
```

## 核心源码

### data.py - 数据获取模块

```python
"""
行情数据获取核心模块
提供两种连接模式：
1. 自动连接模式（默认）：无需任何配置，自动连接本地运行的QMT客户端
2. 自定义连接模式：手动指定QMT路径/端口，适用于多实例/特殊部署场景
"""
import json
import csv
from datetime import datetime
from pathlib import Path
import pandas as pd
from .config import load_config

config = load_config()
_initialized = False
xtdata = None  # xtquant模块实例

def init_default() -> None:
    """
    【推荐】默认连接工厂，无需任何参数，自动连接本地运行的QMT客户端
    适合99%的常规使用场景，本地启动QMT后直接调用即可
    """
    global _initialized, xtdata
    if _initialized:
        return
    
    from xtquant import xtdata as _xtdata
    xtdata = _xtdata
    _initialized = True
    print("已自动连接本地QMT服务")

def init_custom(bin_path: str, port: int = None) -> None:
    """
    自定义连接工厂，适用于特殊场景
    """
    global _initialized, xtdata
    if _initialized:
        return
    
    import sys
    if bin_path not in sys.path:
        sys.path.insert(0, bin_path)
    
    from xtquant import xtdata as _xtdata
    if port:
        _xtdata.set_connect_port(port)
    
    xtdata = _xtdata
    _initialized = True
    print(f"已连接自定义QMT服务：路径={bin_path}" + (f" 端口={port}" if port else ""))

def _ensure_initialized() -> None:
    """内部方法：确保QMT已初始化，自动选择连接模式"""
    global _initialized
    if _initialized:
        return
    
    if config["qmt"]["bin_path"]:
        init_custom(bin_path=config["qmt"]["bin_path"], port=config["qmt"]["port"])
    else:
        init_default()

def get_kline_data(
    stock_list: list, 
    period: str = "1d", 
    start_time: str = None, 
    end_time: str = None, 
    download: bool = True
) -> dict:
    """
    获取K线行情数据
    """
    _ensure_initialized()
    
    if not end_time:
        end_time = datetime.now().strftime("%Y%m%d")
    
    if download:
        xtdata.download_history_data2(
            stock_list=stock_list,
            period=period,
            start_time=start_time,
            end_time=end_time
        )
    
    raw_data = xtdata.get_market_data_ex(
        stock_list=stock_list,
        period=period,
        start_time=start_time,
        end_time=end_time
    )
    
    result = {}
    for stock_code, df in raw_data.items():
        df = df.reset_index()
        df["trade_time"] = df["time"].apply(
            lambda x: datetime.fromtimestamp(x/1000).strftime("%Y-%m-%d %H:%M:%S")
        )
        df = df.drop(columns=["time"])
        df = df.rename(columns={
            "open": "open_price",
            "high": "high_price",
            "low": "low_price",
            "close": "close_price",
            "volume": "trade_volume",
            "amount": "trade_amount"
        })
        result[stock_code] = df.to_dict("records")
    
    return result
```

### cli.py - 命令行入口

```python
"""
命令行入口（基于Cyclopts框架）
"""
import json
from cyclopts import App, Parameter
from typing import Annotated, Optional, List
from .config import load_config
from .data import get_kline_data, save_data

app = App(
    name="qmt",
    help="QMT行情数据连接器",
    version="0.1.0"
)

@app.command(help="测试QMT连接是否正常")
def test_connect():
    try:
        config = load_config()
        print("配置加载成功")
        print(f"QMT bin路径: {config['qmt']['bin_path']}")
        
        test_data = get_kline_data(
            stock_list=["600519.SH"],
            period="1d",
            start_time="20240101",
            end_time="20240110"
        )
        
        if test_data and "600519.SH" in test_data:
            print("行情接口调用成功")
            print(f"测试获取600519.SH数据，共{len(test_data['600519.SH'])}条K线")
            print("连接测试通过！")
        else:
            print("行情数据获取失败")
            exit(1)
            
    except Exception as e:
        print(f"连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

@app.command(help="获取行情数据")
def get_data(
    stocks: Annotated[List[str], Parameter(name=["--stocks", "-s"])],
    period: Annotated[str, Parameter(name=["--period", "-p"])] = "1d",
    start: Annotated[Optional[str], Parameter(name=["--start", "-st"])] = None,
    end: Annotated[Optional[str], Parameter(name=["--end", "-e"])] = None,
    output: Annotated[Optional[str], Parameter(name=["--output", "-o"])] = None,
    format: Annotated[Optional[str], Parameter(name=["--format", "-f"])] = None,
    no_download: Annotated[bool, Parameter(name=["--no-download"])] = False,
):
    data = get_kline_data(
        stock_list=stocks,
        period=period,
        start_time=start,
        end_time=end,
        download=not no_download
    )
    
    if output or load_config()["output"]["save_to_file"]:
        save_path = save_data(data, output, format)
        print(f"数据已保存到: {save_path}")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
```

## pyproject.toml 配置

```toml
[project]
name = "qmt-connector"
version = "0.1.0"
description = "QMT行情数据连接器，符合研究框架标准的可移植工具"
authors = [{ name = "ChenPeng" }]
requires-python = ">=3.10, <3.13"
dependencies = [
    "xtquant>=250516.1.1",
    "pandas >=2.0.0",
    "numpy >=1.24.0",
    "pyyaml >=6.0",
    "tomli >=2.0.1; python_version < '3.11'",
    "tomli-w >=1.0.0",
    "cyclopts >=2.0.0",
]

[project.scripts]
qmt = "qmt_connector.cli:app"

[[tool.uv.index]]
name = "tsinghua"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

## 设计亮点

1. **工厂函数清晰分离**: `init_default()`和`init_custom()`两个明确的入口
2. **0配置开箱即用**: 99%场景不需要修改任何配置，启动QMT直接调用
3. **完全可移植**: 无硬编码路径，复制到其他机器只需要`uv sync`
4. **自动初始化**: 调用数据接口时自动判断连接模式，不需要手动初始化
5. **单例设计**: 连接只会初始化一次，重复调用不会重复创建连接

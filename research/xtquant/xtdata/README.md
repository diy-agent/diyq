# xtquant 数据接口文档

> 来源: [迅投知识库](https://dict.thinktrader.net/nativeApi/start_now.html)  
> 更新时间: 2026-04-19

---

## 简介

XtQuant是基于迅投MiniQMT衍生出来的一套完善的Python策略运行框架，对外以Python库的形式提供策略交易所需要的行情和交易相关的API接口。

**运行依赖**: 在运行使用 XtQuant 的程序前需要先启动 MiniQMT 客户端。

**支持版本**: 64 位 Python 3.6、3.7、3.8、3.9、3.10、3.11、3.12

---

## 📊 数据粒度（时间周期）

xtquant 支持从**分笔（Tick）到年线**的多种粒度：

| 周期代码 | 说明 |
|---------|------|
| `tick` | 分笔数据（逐笔成交明细） |
| `1m` | 1分钟线 |
| `3m` | 3分钟线 |
| `5m` | 5分钟线 |
| `15m` | 15分钟线 |
| `30m` | 30分钟线 |
| `1h` | 小时线 |
| `1d` | 日线 |
| `1w` | 周线 |
| `1mon` | 月线 |
| `1q` | 季线 |
| `1hy` | 半年线 |
| `1y` | 年线 |

---

## 📈 数据类型

### 一、行情数据模块 (XtData)

#### 1.1 K线数据字段

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `close` | 收盘价 |
| `volume` | 成交量 |
| `amount` | 成交额 |
| `settlementPrice` | 今结算 |
| `openInterest` | 持仓量 |
| `preClose` | 前收价 |
| `suspendFlag` | 停牌标记 (0-正常, 1-停牌, -1-当日起复牌) |

#### 1.2 分笔数据(Tick)字段

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `lastPrice` | 最新价 |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `lastClose` | 前收盘价 |
| `amount` | 成交总额 |
| `volume` | 成交总量 |
| `pvolume` | 原始成交总量 |
| `stockStatus` | 证券状态 |
| `openInt` | 持仓量 |
| `lastSettlementPrice` | 前结算 |
| `askPrice` | 委卖价 |
| `bidPrice` | 委买价 |
| `askVol` | 委卖量 |
| `bidVol` | 委买量 |
| `transactionNum` | 成交笔数 |

#### 1.3 除权数据字段

| 字段名 | 说明 |
|-------|------|
| `interest` | 每股股利（税前，元） |
| `stockBonus` | 每股红股（股） |
| `stockGift` | 每股转增股本（股） |
| `allotNum` | 每股配股数（股） |
| `allotPrice` | 配股价格（元） |
| `gugai` | 是否股改 |
| `dr` | 除权系数 |

#### 1.4 Level2 数据（需开通权限）

| 数据类型 | 说明 | 主要字段 |
|---------|------|---------|
| `l2quote` | Level2实时行情快照 | 十档买卖盘、最新价、成交量、持仓量 |
| `l2order` | Level2逐笔委托 | 时间、委托价、委托量、委托号、委托类型、委托方向 |
| `l2transaction` | Level2逐笔成交 | 时间、成交价、成交量、成交号、买卖委托号、成交标志 |
| `l2quoteaux` | Level2实时行情补充 | 委买/委卖均价、总量、撤单统计 |
| `l2orderqueue` | Level2一档委托队列 | 委买/委卖价、量、数量 |

**Level2数据权限说明**: 获取lv2数据时需要数据终端有lv2数据权限

---

### 二、财务数据

支持8大类财务报表：

| 表名 | 说明 |
|-----|------|
| `Balance` | 资产负债表 |
| `Income` | 利润表 |
| `CashFlow` | 现金流量表 |
| `Capital` | 股本表 |
| `Holdernum` | 股东数 |
| `Top10holder` | 十大股东 |
| `Top10flowholder` | 十大流通股东 |
| `Pershareindex` | 每股指标（EPS、ROE、毛利率等） |

---

### 三、合约基础信息

| 字段类别 | 包含信息 |
|---------|---------|
| 基础信息 | 合约代码、名称、市场、品种ID、交易所代码、统一规则代码 |
| 日期信息 | 上市日期、IPO日期、退市日/到期日 |
| 价格信息 | 前收盘、前结算、涨停价、跌停价、最小变动单位 |
| 股本信息 | 流通股本、总股本 |
| 期货/期权特有 | 保证金率、合约乘数、主力合约标记、手续费、期权类型、行权价 |
| 状态信息 | 合约停牌状态、是否可交易、是否近月合约 |

**合约类型支持**: 股票、指数、基金、ETF、期货、期权、可转债等

---

### 四、市场分类数据

| 数据类别 | 说明 |
|---------|------|
| 板块数据 | 板块列表、板块成分股、自定义板块管理 |
| 指数数据 | 指数成分股权重信息 |
| 可转债 | 可转债基础信息、转股信息 |
| ETF | ETF申赎清单信息 |
| 新股 | 新股申购信息、申购额度 |
| 日历 | 交易日历、节假日数据 |

---

## 🔧 核心接口概览

### 行情接口 (xtdata)

```python
# 获取行情数据
get_market_data(field_list, stock_list, period, start_time, end_time, count)

# 订阅实时行情
subscribe_quote(stock_code, period, callback)

# 下载历史数据
download_history_data(stock_code, period, start_time, end_time)

# 获取财务数据
get_financial_data(stock_list, table_list, start_time, end_time)

# 获取合约信息
get_instrument_detail(stock_code)

# 获取板块成分股
get_stock_list_in_sector(sector_name)
```

---

## ⚠️ 重要说明

1. **Level2数据**: 需要数据终端有相应的权限才能获取
2. **MiniQMT客户端**: 必须先启动才能使用 xtquant
3. **本地数据**: 需先通过 `download_history_data` 接口下载历史数据
4. **复权方式**: 支持不复权、前复权、后复权、等比前复权、等比后复权
5. **Python版本**: 仅支持 64位 Python 3.6-3.12

---

## 🔗 官方文档

- [快速入门](https://dict.thinktrader.net/nativeApi/start_now.html)
- [行情模块文档](https://dict.thinktrader.net/nativeApi/xtdata.html)
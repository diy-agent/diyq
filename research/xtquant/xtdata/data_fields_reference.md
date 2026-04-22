# xtquant 数据字段参考表

> 快速查阅版 - 来自官方文档整理

---

## Tick 分笔数据字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `time` | int | 时间戳 |
| `lastPrice` | float | 最新价 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `lastClose` | float | 前收盘价 |
| `amount` | float | 成交总额 |
| `volume` | int | 成交总量 |
| `pvolume` | int | 原始成交总量 |
| `stockStatus` | int | 证券状态 |
| `openInt` | int | 持仓量 |
| `lastSettlementPrice` | float | 前结算 |
| `askPrice` | list | 委卖价 |
| `bidPrice` | list | 委买价 |
| `askVol` | list | 委卖量 |
| `bidVol` | list | 委买量 |
| `transactionNum` | int | 成交笔数 |

---

## K线数据字段 (1m/5m/1d等)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `time` | int | 时间戳 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `volume` | int | 成交量 |
| `amount` | float | 成交额 |
| `settlementPrice` | float | 今结算 |
| `openInterest` | int | 持仓量 |
| `preClose` | float | 前收价 |
| `suspendFlag` | int | 停牌标记 (0-正常, 1-停牌, -1-当日起复牌) |

---

## Level2 行情快照 (l2quote)

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `lastPrice` | 最新价 |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `amount` | 成交额 |
| `volume` | 成交总量 |
| `pvolume` | 原始成交总量 |
| `openInt` | 持仓量 |
| `stockStatus` | 证券状态 |
| `transactionNum` | 成交笔数 |
| `lastClose` | 前收盘价 |
| `lastSettlementPrice` | 前结算 |
| `settlementPrice` | 今结算 |
| `pe` | 市盈率 |
| `askPrice` | 多档委卖价 |
| `bidPrice` | 多档委买价 |
| `askVol` | 多档委卖量 |
| `bidVol` | 多档委买量 |

---

## Level2 逐笔委托 (l2order)

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `price` | 委托价 |
| `volume` | 委托量 |
| `entrustNo` | 委托号 |
| `entrustType` | 委托类型 |
| `entrustDirection` | 委托方向 (1-买入, 2-卖出, 3-撤买, 4-撤卖) |

---

## Level2 逐笔成交 (l2transaction)

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `price` | 成交价 |
| `volume` | 成交量 |
| `amount` | 成交额 |
| `tradeIndex` | 成交记录号 |
| `buyNo` | 买方委托号 |
| `sellNo` | 卖方委托号 |
| `tradeType` | 成交类型 |
| `tradeFlag` | 成交标志 (1-外盘, 2-内盘, 3-撤单) |

---

## Level2 行情补充 (l2quoteaux)

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `avgBidPrice` | 委买均价 |
| `totalBidQuantity` | 委买总量 |
| `avgOffPrice` | 委卖均价 |
| `totalOffQuantity` | 委卖总量 |
| `withdrawBidQuantity` | 买入撤单总量 |
| `withdrawBidAmount` | 买入撤单总额 |
| `withdrawOffQuantity` | 卖出撤单总量 |
| `withdrawOffAmount` | 卖出撤单总额 |

---

## Level2 委托队列 (l2orderqueue)

| 字段名 | 说明 |
|-------|------|
| `time` | 时间戳 |
| `bidLevelPrice` | 委买价 |
| `bidLevelVolume` | 委买量 |
| `offerLevelPrice` | 委卖价 |
| `offerLevelVolume` | 委卖量 |
| `bidLevelNumber` | 委买数量 |
| `offLevelNumber` | 委卖数量 |

---

## 除权数据字段

| 字段名 | 说明 |
|-------|------|
| `interest` | 每股股利（税前，元） |
| `stockBonus` | 每股红股（股） |
| `stockGift` | 每股转增股本（股） |
| `allotNum` | 每股配股数（股） |
| `allotPrice` | 配股价格（元） |
| `gugai` | 是否股改 |
| `dr` | 除权系数 |

---

## 证券状态字典

| 值 | 含义 |
|---|------|
| 0,10 | 默认为未知 |
| 11 | 开盘前S |
| 12 | 集合竞价时段C |
| 13 | 连续交易T |
| 14 | 休市B |
| 15 | 闭市E |
| 16 | 波动性中断V |
| 17 | 临时停牌P |
| 18 | 收盘集合竞价U |
| 19 | 盘中集合竞价M |
| 20 | 暂停交易至闭市N |
| 21 | 获取字段异常 |
| 22 | 盘后固定价格行情 |
| 23 | 盘后固定价格行情完毕 |

---

## 委托状态字典

| 值 | 含义 |
|---|------|
| 48 | 未报 |
| 49 | 待报 |
| 50 | 已报 |
| 51 | 已报待撤 |
| 52 | 部成待撤 |
| 53 | 部撤 |
| 54 | 已撤 |
| 55 | 部成 |
| 56 | 已成 |
| 57 | 废单 |
| 255 | 未知 |

---

## 复权方式

| 代码 | 说明 |
|-----|------|
| `none` | 不复权 |
| `front` | 向前复权 |
| `back` | 向后复权 |
| `front_ratio` | 等比向前复权 |
| `back_ratio` | 等比向后复权 |

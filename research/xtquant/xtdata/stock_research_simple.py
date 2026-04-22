# -*- coding: utf-8 -*-

# %% s单元格1

"""
Stock Research Notebook - 简化版 (无ipywidgets依赖)
===================================================
使用方法: 在 Jupyter/JupyterLab 或 Python 脚本中逐段运行

依赖: pandas, matplotlib, xtquant
"""
# %% s单元格1

import pandas as pd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# CELL 0: 初始化
# =============================================================================
print("=" * 60)
print("Cell 0: 初始化")
print("=" * 60)

s
import xtquant.xtdata as xtdata
client = xtdata.connect()
print(f"[OK] 已连接 MiniQMT")

# 下载板块数据
try:
    xtdata.download_sector_data()
    print("[OK] 板块数据已同步")
except:
    pass

# 全局状态
WATCHLIST = []          # [(code, name), ...]
DOWNLOAD_STATUS = {}    # {code: {'downloaded': bool, 'bars': int}}
KLINE_CACHE = {}        # {code: DataFrame}
STOCK_REGISTRY = {}     # {code: name}

# 加载股票列表
print("\n[加载股票列表...]")
for sector in ["沪深A股", "沪市A股", "深市A股"]:
    codes = xtdata.get_stock_list_in_sector(sector)
    if codes:
        print(f"  从 '{sector}' 获取 {len(codes)} 只股票")
        for code in codes[:300]:  # 限制数量加快速度
            try:
                info = xtdata.get_instrument_detail(code)
                if info:
                    STOCK_REGISTRY[code] = info.get('InstrumentName', '未知')
            except:
                pass
        break

print(f"[OK] 已加载 {len(STOCK_REGISTRY)} 只股票")


# =============================================================================
# CELL 1: 搜索与关注列表管理 (函数形式)
# =============================================================================
print("\n" + "=" * 60)
print("Cell 1: 股票搜索与关注列表")
print("=" * 60)


def search_stocks(keyword, limit=20):
    """
    按关键字搜索股票
    
    用法:
        results = search_stocks('银行')
        results = search_stocks('600000')
    """
    matches = []
    for code, name in STOCK_REGISTRY.items():
        if keyword.lower() in code.lower() or keyword.lower() in name.lower():
            matches.append((code, name))
    
    matches = matches[:limit]
    
    print(f"\n搜索结果 '{keyword}' ({len(matches)} 只):")
    print("-" * 40)
    for i, (code, name) in enumerate(matches, 1):
        print(f"  {i}. {code} - {name}")
    
    return matches


def add_to_watchlist(code_or_list):
    """
    添加股票到关注列表
    
    用法:
        add_to_watchlist('600000.SH')
        add_to_watchlist(['600000.SH', '000001.SZ'])
    """
    if isinstance(code_or_list, str):
        codes = [code_or_list]
    else:
        codes = code_or_list
    
    added = 0
    for code in codes:
        name = STOCK_REGISTRY.get(code, '未知')
        if (code, name) not in WATCHLIST:
            WATCHLIST.append((code, name))
            added += 1
            print(f"  [+] {code} {name}")
    
    print(f"\n[OK] 已添加 {added} 只，关注列表共 {len(WATCHLIST)} 只")


def remove_from_watchlist(code_or_list):
    """
    从关注列表移除股票
    
    用法:
        remove_from_watchlist('600000.SH')
    """
    if isinstance(code_or_list, str):
        codes = [code_or_list]
    else:
        codes = code_or_list
    
    removed = 0
    for code in codes:
        for i, (c, n) in enumerate(WATCHLIST):
            if c == code:
                WATCHLIST.pop(i)
                if code in DOWNLOAD_STATUS:
                    del DOWNLOAD_STATUS[code]
                if code in KLINE_CACHE:
                    del KLINE_CACHE[code]
                removed += 1
                print(f"  [-] {code} {n}")
                break
    
    print(f"\n[OK] 已移除 {removed} 只，关注列表共 {len(WATCHLIST)} 只")


def show_watchlist():
    """
    显示当前关注列表及状态
    """
    print(f"\n当前关注列表 ({len(WATCHLIST)} 只):")
    print("-" * 60)
    print(f"{'序号':<4} {'代码':<12} {'名称':<10} {'状态':<10} {'数据条数':<8}")
    print("-" * 60)
    
    for i, (code, name) in enumerate(WATCHLIST, 1):
        status = DOWNLOAD_STATUS.get(code, {})
        downloaded = '✓ 已下载' if status.get('downloaded') else '○ 未下载'
        bars = status.get('bars', 0)
        print(f"{i:<4} {code:<12} {name:<10} {downloaded:<10} {bars:<8}")


# 演示搜索功能
print("\n[示例] 搜索包含'银行'的股票:")
results = search_stocks('银行', limit=10)


# =============================================================================
# CELL 2: 下载日行情
# =============================================================================
print("\n" + "=" * 60)
print("Cell 2: 下载日行情数据")
print("=" * 60)


def download_watchlist_data(days=365):
    """
    下载关注列表所有股票的日线数据
    
    用法:
        download_watchlist_data(180)  # 下载最近180天
    """
    if not WATCHLIST:
        print("[WARN] 关注列表为空，请先添加股票")
        return
    
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    print(f"\n下载参数:")
    print(f"  股票数: {len(WATCHLIST)}")
    print(f"  日期: {start_date} ~ {end_date}")
    
    # 下载
    print("\n[下载中...]")
    for i, (code, name) in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] {code} {name}...", end=' ')
        try:
            xtdata.download_history_data(code, '1d', start_date, end_date)
            DOWNLOAD_STATUS[code] = {'downloaded': True, 'bars': 0}
            print("OK")
        except Exception as e:
            DOWNLOAD_STATUS[code] = {'downloaded': False, 'error': str(e)}
            print(f"FAIL")
    
    # 读取统计
    print("\n[读取数据...]")
    for code, name in WATCHLIST:
        if not DOWNLOAD_STATUS[code]['downloaded']:
            continue
        try:
            data = xtdata.get_market_data(
                field_list=[],
                stock_list=[code],
                period='1d',
                start_time=start_date,
                end_time=end_date
            )
            
            if data and code in data:
                df = data[code]
                if 'time' in df.columns:
                    df['date'] = pd.to_datetime(df['time'], unit='ms')
                    df = df.set_index('date').sort_index()
                KLINE_CACHE[code] = df
                DOWNLOAD_STATUS[code]['bars'] = len(df)
        except Exception as e:
            DOWNLOAD_STATUS[code]['error'] = str(e)
    
    # 显示结果
    show_watchlist()


# 快速添加测试股票并下载
print("\n[快速测试] 添加几只银行股票...")
test_codes = ['600000.SH', '000001.SZ']
for code in test_codes:
    if code in STOCK_REGISTRY:
        add_to_watchlist(code)

# 如果用户之前已经添加了股票，就下载它们
if WATCHLIST:
    download_watchlist_data(days=180)


# =============================================================================
# CELL 3: K线对比图
# =============================================================================
print("\n" + "=" * 60)
print("Cell 3: K线对比图")
print("=" * 60)


def plot_comparison(codes=None, days=90, normalize=True, show_volume=True):
    """
    绘制多股票K线对比图
    
    参数:
        codes: 股票代码列表，None表示使用所有已下载的关注股票
        days: 显示最近多少天的数据
        normalize: True=归一化对比(基准100)，False=原始价格
        show_volume: 是否显示成交量子图
    
    用法:
        plot_comparison()  # 绘制所有关注股票
        plot_comparison(['600000.SH', '000001.SZ'], days=60)
        plot_comparison(normalize=False)  # 原始价格对比
    """
    # 确定要绘制的股票
    if codes is None:
        codes = [code for code, _ in WATCHLIST 
                if DOWNLOAD_STATUS.get(code, {}).get('downloaded')]
    
    if not codes:
        print("[WARN] 没有可用的股票数据")
        return
    
    # 创建子图
    if show_volume:
        fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(14, 8), 
                                                gridspec_kw={'height_ratios': [3, 1]})
    else:
        fig, ax_price = plt.subplots(figsize=(14, 6))
        ax_vol = None
    
    colors = plt.cm.tab10.colors
    valid_codes = []
    
    for i, code in enumerate(codes):
        if code not in KLINE_CACHE:
            print(f"[SKIP] {code} 无缓存数据")
            continue
        
        df = KLINE_CACHE[code].tail(days).copy()
        if df.empty or 'close' not in df.columns:
            continue
        
        valid_codes.append(code)
        name = next((n for c, n in WATCHLIST if c == code), code)
        color = colors[i % len(colors)]
        
        close = df['close'].dropna()
        if len(close) < 2:
            continue
        
        # 绘制价格线
        if normalize:
            y = close / close.iloc[0] * 100
            label = f"{code} {name} ({close.iloc[-1]/close.iloc[0]-1:+.1%})"
            ax_price.set_ylabel('归一化价格 (基准=100)')
        else:
            y = close
            label = f"{code} {name}"
            ax_price.set_ylabel('收盘价')
        
        ax_price.plot(y.index, y.values, label=label, 
                     color=color, linewidth=1.5, marker='o', markersize=2)
        
        # 绘制成交量
        if show_volume and ax_vol is not None and 'volume' in df.columns:
            vol = df['volume'].dropna()
            if len(vol) > 0 and vol.max() > 0:
                vol_norm = vol / vol.max() * 100
                ax_vol.bar(df.index, vol_norm, alpha=0.3, color=color, width=0.8)
    
    # 设置图表
    title_type = '归一化对比' if normalize else '原始价格对比'
    ax_price.set_title(f'K线{title_type}图 ({days}日)', fontsize=14)
    ax_price.legend(loc='upper left', fontsize=9)
    ax_price.grid(True, alpha=0.3)
    
    if normalize:
        ax_price.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    if show_volume and ax_vol is not None:
        ax_vol.set_ylabel('成交量 (归一化 %)')
        ax_vol.set_xlabel('日期')
        ax_vol.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 显示统计表格
    if valid_codes:
        print("\n" + "=" * 60)
        print("选中股票统计")
        print("=" * 60)
        stats = []
        for code in valid_codes:
            df = KLINE_CACHE[code].tail(days)
            name = next((n for c, n in WATCHLIST if c == code), code)
            close = df['close'].dropna()
            if len(close) >= 2:
                stats.append({
                    '代码': code,
                    '名称': name,
                    '最新价': f"{close.iloc[-1]:.2f}",
                    '区间涨跌': f"{(close.iloc[-1]/close.iloc[0]-1)*100:+.2f}%",
                    '最高价': f"{close.max():.2f}",
                    '最低价': f"{close.min():.2f}",
                    '日均成交': f"{df['volume'].mean()/1e4:.0f}万" if 'volume' in df.columns else '-"
                })
        
        display(pd.DataFrame(stats))


def plot_candlestick(code, days=60):
    """
    绘制单只股票的K线图 (OHLC)
    
    用法:
        plot_candlestick('600000.SH', days=30)
    """
    if code not in KLINE_CACHE:
        print(f"[WARN] {code} 无数据")
        return
    
    df = KLINE_CACHE[code].tail(days).copy()
    name = next((n for c, n in WATCHLIST if c == code), code)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    
    # 绘制K线 (简化版)
    for i, (idx, row) in enumerate(df.iterrows()):
        color = 'red' if row['close'] >= row['open'] else 'green'
        
        # 实体
        ax1.bar(idx, row['close'] - row['open'], bottom=row['open'], 
               color=color, width=0.6, edgecolor=color)
        
        # 影线
        ax1.plot([idx, idx], [row['low'], row['high']], color=color, linewidth=0.5)
    
    ax1.set_title(f'{code} {name} - K线图 ({days}日)', fontsize=14)
    ax1.set_ylabel('价格')
    ax1.grid(True, alpha=0.3)
    
    # 成交量
    if 'volume' in df.columns:
        colors = ['red' if c >= o else 'green' 
                 for c, o in zip(df['close'], df['open'])]
        ax2.bar(df.index, df['volume'], color=colors, alpha=0.7, width=0.6)
        ax2.set_ylabel('成交量')
        ax2.set_xlabel('日期')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# 使用说明
print("""
[使用指南]

1. 搜索股票:
   results = search_stocks('银行')      # 按名称搜索
   results = search_stocks('600000')    # 按代码搜索

2. 管理关注列表:
   add_to_watchlist('600000.SH')                    # 添加单只
   add_to_watchlist(['600000.SH', '000001.SZ'])     # 批量添加
   remove_from_watchlist('600000.SH')               # 移除
   show_watchlist()                                  # 查看列表

3. 下载数据:
   download_watchlist_data(180)  # 下载180天日线

4. 绘制图表:
   plot_comparison()               # 对比所有关注股票
   plot_comparison(days=60)        # 最近60天
   plot_comparison(normalize=False) # 原始价格
   plot_candlestick('600000.SH')   # 单股票K线图
""")

# 自动演示 (如果有数据)
available = [c for c, _ in WATCHLIST if c in KLINE_CACHE]
if len(available) >= 2:
    print("\n[自动演示] 绘制前两只股票的对比图:")
    plot_comparison(available[:2], days=60)
elif len(available) == 1:
    print("\n[自动演示] 绘制单只股票K线图:")
    plot_candlestick(available[0], days=60)
else:
    print("\n[提示] 请先添加股票并下载数据，然后运行 plot_comparison()")


print("\n" + "=" * 60)
print("Notebook 加载完成!")
print("=" * 60)

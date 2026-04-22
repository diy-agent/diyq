# -*- coding: utf-8 -*-
"""
Stock Research Notebook - Pure Python Version
=============================================
使用方法: 在 Jupyter/JupyterLab 中逐 Cell 运行

Cell 1: 搜索股票并添加到关注列表
Cell 2: 下载日行情并显示状态
Cell 3: 多选K线对比图
"""
# %% 单元格1

import pandas as pd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta
from IPython.display import display, HTML

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ## CELL 0: 初始化 (必须首先运行)

# %% x
print("=" * 60)
print("Cell 0: 初始化 xtquant 环境")
print("=" * 60)
# %% 单元格2

try:
    import xtquant.xtdata as xtdata
    client = xtdata.connect()
    print(f"[OK] 已连接 MiniQMT: {type(client).__name__}")
    
    # 下载板块数据
    try:
        xtdata.download_sector_data()
        print("[OK] 板块数据已同步")
    except Exception as e:
        print(f"[WARN] 板块数据同步: {e}")
except Exception as e:
    print(f"[FAIL] 连接失败: {e}")
    raise

# %% 单元格2


# 全局状态存储
WATCHLIST = []          # 关注列表: [(code, name), ...]
DOWNLOAD_STATUS = {}    # 下载状态: {code: {'downloaded': bool, 'bars': int}}
KLINE_CACHE = {}        # K线缓存: {code: DataFrame}
STOCK_REGISTRY = {}     # 股票注册表: {code: name}

# 加载全量股票列表
print("\n[加载股票列表...]")
for sector in ["沪深A股", "沪市A股", "深市A股", "深证100"]:
    codes = xtdata.get_stock_list_in_sector(sector)
    if codes:
        print(f"  从 '{sector}' 获取 {len(codes)} 只股票")
        # 批量获取名称 (只获取前500只避免太慢)
        for code in codes[:500]:
            try:
                info = xtdata.get_instrument_detail(code)
                if info:
                    STOCK_REGISTRY[code] = info.get('InstrumentName', '未知')
            except:
                pass
        break

print(f"[OK] 已加载 {len(STOCK_REGISTRY)} 只股票到注册表")
print("\n" + "=" * 60)
print("初始化完成，可以继续运行 Cell 1")
print("=" * 60)


# =============================================================================
# CELL 1: 股票搜索与关注列表管理
# =============================================================================
print("=" * 60)
print("Cell 1: 股票搜索与关注列表")
print("=" * 60)

try:
    from ipywidgets import widgets, Layout, HBox, VBox, interact
    from IPython.display import clear_output
    
    # 搜索输出区域
    search_output = widgets.Output()
    watchlist_output = widgets.Output()
    
    # 搜索框
    search_box = widgets.Text(
        placeholder='输入股票名称或代码关键字 (如: 银行、600000、平安)',
        layout=Layout(width='400px')
    )
    
    # 搜索结果选择器
    result_selector = widgets.SelectMultiple(
        options=[],
        description='搜索结果:',
        layout=Layout(width='400px', height='150px'),
        disabled=True
    )
    
    # 添加按钮
    add_btn = widgets.Button(
        description='添加到关注',
        button_style='primary',
        disabled=True
    )
    
    # 关注列表显示
    watchlist_display = widgets.SelectMultiple(
        options=[],
        description='关注列表:',
        layout=Layout(width='400px', height='150px')
    )
    
    # 移除按钮
    remove_btn = widgets.Button(
        description='移除选中',
        button_style='warning'
    )
    
    # 搜索函数
    def on_search(change):
        keyword = change['new'].strip()
        with search_output:
            clear_output()
            if len(keyword) < 1:
                result_selector.options = []
                result_selector.disabled = True
                add_btn.disabled = True
                return
            
            # 搜索匹配的股票
            matches = []
            for code, name in STOCK_REGISTRY.items():
                if keyword.lower() in code.lower() or keyword.lower() in name.lower():
                    matches.append((code, name))
            
            # 限制显示数量
            matches = matches[:50]
            
            if matches:
                result_selector.options = [f"{code} - {name}" for code, name in matches]
                result_selector.disabled = False
                add_btn.disabled = False
                print(f"找到 {len(matches)} 只匹配股票 (最多显示50只)")
            else:
                result_selector.options = []
                result_selector.disabled = True
                add_btn.disabled = True
                print("未找到匹配的股票")
    
    # 添加关注
    def on_add_click(b):
        selected = result_selector.value
        for item in selected:
            code = item.split(' - ')[0]
            name = item.split(' - ')[1]
            if (code, name) not in WATCHLIST:
                WATCHLIST.append((code, name))
        update_watchlist_display()
        print(f"[OK] 已添加 {len(selected)} 只股票到关注列表")
    
    # 移除关注
    def on_remove_click(b):
        selected = watchlist_display.value
        to_remove = []
        for item in selected:
            code = item.split(' - ')[0]
            name = item.split(' - ')[1]
            to_remove.append((code, name))
        
        for item in to_remove:
            WATCHLIST.remove(item)
            # 清理缓存
            if item[0] in DOWNLOAD_STATUS:
                del DOWNLOAD_STATUS[item[0]]
            if item[0] in KLINE_CACHE:
                del KLINE_CACHE[item[0]]
        
        update_watchlist_display()
        print(f"[OK] 已移除 {len(to_remove)} 只股票")
    
    # 更新关注列表显示
    def update_watchlist_display():
        watchlist_display.options = [f"{code} - {name}" for code, name in WATCHLIST]
    
    # 绑定事件
    search_box.observe(on_search, names='value')
    add_btn.on_click(on_add_click)
    remove_btn.on_click(on_remove_click)
    
    # 显示界面
    display(HTML("<h3>🔍 股票搜索</h3>"))
    display(search_box)
    display(search_output)
    display(HBox([result_selector, VBox([add_btn, remove_btn])]))
    
    display(HTML("<h3>📋 我的关注列表</h3>"))
    display(watchlist_display)
    
    # 显示当前状态
    if WATCHLIST:
        update_watchlist_display()
        print(f"\n当前关注 {len(WATCHLIST)} 只股票")
    else:
        print("\n关注列表为空，请搜索添加股票")
        
except ImportError:
    print("[WARN] 未安装 ipywidgets，使用简化版命令行界面")
    print("\n可用命令:")
    print("  search('关键字')  - 搜索股票")
    print("  add('代码')       - 添加到关注列表")
    print("  remove('代码')    - 从关注列表移除")
    print("  show_watchlist()  - 显示关注列表")
    
    def search(keyword):
        """搜索股票"""
        matches = [(c, n) for c, n in STOCK_REGISTRY.items() 
                   if keyword.lower() in c.lower() or keyword.lower() in n.lower()][:20]
        print(f"\n找到 {len(matches)} 只匹配股票:")
        for code, name in matches:
            print(f"  {code} - {name}")
        return matches
    
    def add(code):
        """添加股票到关注列表"""
        name = STOCK_REGISTRY.get(code, '未知')
        if (code, name) not in WATCHLIST:
            WATCHLIST.append((code, name))
            print(f"[OK] 已添加: {code} {name}")
        else:
            print(f"[WARN] 已在关注列表中")
        show_watchlist()
    
    def remove(code):
        """从关注列表移除"""
        for i, (c, n) in enumerate(WATCHLIST):
            if c == code:
                WATCHLIST.pop(i)
                if code in DOWNLOAD_STATUS:
                    del DOWNLOAD_STATUS[code]
                if code in KLINE_CACHE:
                    del KLINE_CACHE[code]
                print(f"[OK] 已移除: {code}")
                break
        show_watchlist()
    
    def show_watchlist():
        """显示关注列表"""
        print(f"\n当前关注列表 ({len(WATCHLIST)} 只):")
        for code, name in WATCHLIST:
            status = DOWNLOAD_STATUS.get(code, {}).get('downloaded', False)
            status_str = "✓ 已下载" if status else "○ 未下载"
            print(f"  {code} - {name} [{status_str}]")


# =============================================================================
# CELL 2: 下载日行情并显示状态
# =============================================================================
print("=" * 60)
print("Cell 2: 下载日行情数据")
print("=" * 60)

if not WATCHLIST:
    print("[WARN] 关注列表为空，请先运行 Cell 1 添加股票")
else:
    # 设置下载日期范围
    END_DATE = datetime.now().strftime('%Y%m%d')
    START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    print(f"\n下载参数:")
    print(f"  股票数量: {len(WATCHLIST)} 只")
    print(f"  日期范围: {START_DATE} ~ {END_DATE}")
    print(f"  数据周期: 日线")
    
    # 下载数据
    print("\n[开始下载...]")
    for i, (code, name) in enumerate(WATCHLIST, 1):
        print(f"  [{i}/{len(WATCHLIST)}] {code} {name} ...", end=' ')
        try:
            xtdata.download_history_data(code, '1d', START_DATE, END_DATE)
            DOWNLOAD_STATUS[code] = {'downloaded': True, 'bars': 0}
            print("OK")
        except Exception as e:
            DOWNLOAD_STATUS[code] = {'downloaded': False, 'bars': 0, 'error': str(e)}
            print(f"FAIL: {e}")
    
    # 读取数据并统计
    print("\n[读取数据...]")
    for code, name in WATCHLIST:
        if not DOWNLOAD_STATUS[code]['downloaded']:
            continue
        try:
            data = xtdata.get_market_data(
                field_list=[],
                stock_list=[code],
                period='1d',
                start_time=START_DATE,
                end_time=END_DATE
            )
            
            if data and code in data:
                df = data[code]
                # 转换为标准格式
                if 'time' in df.columns:
                    df['date'] = pd.to_datetime(df['time'], unit='ms')
                    df = df.set_index('date').sort_index()
                KLINE_CACHE[code] = df
                DOWNLOAD_STATUS[code]['bars'] = len(df)
        except Exception as e:
            DOWNLOAD_STATUS[code]['error'] = str(e)
    
    # 显示状态表格
    print("\n" + "=" * 60)
    print("下载状态汇总")
    print("=" * 60)
    
    status_data = []
    for code, name in WATCHLIST:
        status = DOWNLOAD_STATUS.get(code, {})
        status_data.append({
            '股票代码': code,
            '股票名称': name,
            '下载状态': '✓ 成功' if status.get('downloaded') else '✗ 失败',
            '数据条数': status.get('bars', 0),
            '备注': status.get('error', '')[:30]
        })
    
    df_status = pd.DataFrame(status_data)
    display(df_status)
    
    success_count = sum(1 for s in DOWNLOAD_STATUS.values() if s.get('downloaded'))
    print(f"\n[汇总] 成功: {success_count}/{len(WATCHLIST)} 只")
    
    if success_count == 0:
        print("[WARN] 没有成功下载的数据，无法继续 Cell 3")


# =============================================================================
# CELL 3: 多选K线对比图
# =============================================================================
print("=" * 60)
print("Cell 3: K线对比图")
print("=" * 60)

# 检查可用数据
available_stocks = [(code, name) for code, name in WATCHLIST 
                    if DOWNLOAD_STATUS.get(code, {}).get('downloaded') and code in KLINE_CACHE]

if not available_stocks:
    print("[WARN] 没有可用的K线数据，请先运行 Cell 2 下载数据")
else:
    print(f"可用股票 ({len(available_stocks)} 只):")
    for code, name in available_stocks:
        print(f"  {code} - {name}")
    
    try:
        from ipywidgets import interact, SelectMultiple, Dropdown
        
        # 创建多选界面
        stock_options = [f"{code} - {name}" for code, name in available_stocks]
        
        @interact(
            selected=SelectMultiple(
                options=stock_options,
                description='选择股票:',
                layout={'width': '400px', 'height': '150px'}
            ),
            chart_type=Dropdown(
                options=['归一化价格对比', '原始价格对比', '涨跌幅对比'],
                description='图表类型:',
                layout={'width': '200px'}
            ),
            days=Dropdown(
                options=[('30天', 30), ('60天', 60), ('90天', 90), ('180天', 180), ('一年', 365)],
                description='时间范围:',
                value=90,
                layout={'width': '150px'}
            )
        )
        def plot_kline(selected, chart_type, days):
            if not selected:
                print("请至少选择一只股票")
                return
            
            # 解析选中的股票
            selected_codes = [s.split(' - ')[0] for s in selected]
            
            # 设置图表
            fig, axes = plt.subplots(2, 1, figsize=(14, 10), 
                                     gridspec_kw={'height_ratios': [3, 1]})
            
            ax_price = axes[0]
            ax_volume = axes[1]
            
            colors = plt.cm.tab10.colors
            
            for i, code in enumerate(selected_codes):
                df = KLINE_CACHE[code]
                name = next((n for c, n in available_stocks if c == code), code)
                
                # 截取最近N天
                df_plot = df.tail(days).copy()
                if df_plot.empty:
                    continue
                
                color = colors[i % len(colors)]
                
                # 根据图表类型处理数据
                if chart_type == '归一化价格对比':
                    close = df_plot['close'].dropna()
                    if len(close) > 0:
                        normalized = close / close.iloc[0] * 100
                        ax_price.plot(normalized.index, normalized.values, 
                                     label=f"{code} {name}", color=color, linewidth=1.5)
                        ax_price.set_ylabel('归一化价格 (基准=100)')
                        ax_price.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
                        
                elif chart_type == '原始价格对比':
                    ax_price.plot(df_plot.index, df_plot['close'], 
                                 label=f"{code} {name}", color=color, linewidth=1.5)
                    ax_price.set_ylabel('收盘价')
                    
                elif chart_type == '涨跌幅对比':
                    close = df_plot['close'].dropna()
                    if len(close) > 0:
                        returns = (close / close.iloc[0] - 1) * 100
                        ax_price.plot(returns.index, returns.values, 
                                     label=f"{code} {name}", color=color, linewidth=1.5)
                        ax_price.set_ylabel('累计涨跌幅 (%)')
                        ax_price.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
                
                # 绘制成交量 (归一化显示)
                if 'volume' in df_plot.columns:
                    vol = df_plot['volume'].dropna()
                    if len(vol) > 0:
                        vol_normalized = vol / vol.max() * 100 if vol.max() > 0 else vol
                        ax_volume.bar(df_plot.index, vol_normalized, alpha=0.3, color=color)
            
            # 设置图表属性
            ax_price.set_title(f'K线对比图 - {chart_type}', fontsize=14)
            ax_price.legend(loc='upper left')
            ax_price.grid(True, alpha=0.3)
            
            ax_volume.set_ylabel('成交量 (归一化)')
            ax_volume.set_xlabel('日期')
            ax_volume.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # 显示统计信息
            print("\n" + "=" * 60)
            print("选中股票统计")
            print("=" * 60)
            stats = []
            for code in selected_codes:
                df = KLINE_CACHE[code]
                df_recent = df.tail(days)
                name = next((n for c, n in available_stocks if c == code), code)
                
                close = df_recent['close'].dropna()
                if len(close) >= 2:
                    stats.append({
                        '股票': f"{code} {name}",
                        '最新价': f"{close.iloc[-1]:.2f}",
                        '区间涨跌': f"{(close.iloc[-1]/close.iloc[0]-1)*100:+.2f}%",
                        '最高': f"{close.max():.2f}",
                        '最低': f"{close.min():.2f}",
                        '波动率': f"{close.pct_change().std()*100:.2f}%"
                    })
            
            if stats:
                display(pd.DataFrame(stats))
    
    except ImportError:
        print("\n[WARN] ipywidgets 未安装，使用简化版")
        print("可用命令: plot(['代码1', '代码2'], days=90)")
        
        def plot(codes, days=90, normalize=True):
            """绘制K线对比图"""
            fig, ax = plt.subplots(figsize=(14, 6))
            colors = plt.cm.tab10.colors
            
            for i, code in enumerate(codes):
                if code not in KLINE_CACHE:
                    print(f"[SKIP] {code} 无数据")
                    continue
                
                df = KLINE_CACHE[code].tail(days)
                name = next((n for c, n in available_stocks if c == code), code)
                color = colors[i % len(colors)]
                
                close = df['close'].dropna()
                if len(close) == 0:
                    continue
                
                if normalize:
                    y = close / close.iloc[0] * 100
                    ax.set_ylabel('归一化价格 (基准=100)')
                    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
                else:
                    y = close
                    ax.set_ylabel('收盘价')
                
                ax.plot(y.index, y.values, label=f"{code} {name}", 
                       color=color, linewidth=1.5)
            
            ax.set_title('K线对比图', fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        
        # 示例
        print("\n示例:")
        print(f"  plot(['{available_stocks[0][0]}', '{available_stocks[-1][0]}'], days=60)")


print("\n" + "=" * 60)
print("Notebook 加载完成")
print("=" * 60)

# %%

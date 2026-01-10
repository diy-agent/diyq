import streamlit as st
import pandas as pd
import os
import sys
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.downloader import DataDownloader
from src.strategy.base import MomentumStrategy, BacktestEngine
from src.utils.config_manager import ConfigManager

st.set_page_config(page_title="轻量级量化交易系统", layout="wide")

config_manager = ConfigManager()

st.title("📈 轻量级量化交易系统")

# 侧边栏配置
st.sidebar.header("配置中心")

# 策略配置保存/加载
st.sidebar.subheader("配置管理")
config_names = config_manager.list_configs()
selected_config = st.sidebar.selectbox("加载现有配置", ["新建配置"] + config_names)

config_name_input = st.sidebar.text_input("当前配置名称", selected_config if selected_config != "新建配置" else "default_strategy")

# 初始值
init_window = 20
init_threshold = 0.05
init_stop_loss = 0.05

if selected_config != "新建配置":
    loaded_config = config_manager.load_config(selected_config)
    if loaded_config:
        init_window = loaded_config.get("window", 20)
        init_threshold = loaded_config.get("threshold", 0.05)
        init_stop_loss = loaded_config.get("stop_loss", 0.05)

# 策略参数
st.sidebar.subheader("策略参数")
window = st.sidebar.slider("动量窗口 (天)", 5, 60, init_window)
threshold = st.sidebar.slider("突破阈值", 0.01, 0.20, init_threshold)
stop_loss = st.sidebar.slider("止损比例", 0.01, 0.10, init_stop_loss)

if st.sidebar.button("保存当前配置"):
    config_manager.save_config(config_name_input, {
        "window": window,
        "threshold": threshold,
        "stop_loss": stop_loss
    })
    st.sidebar.success(f"配置 {config_name_input} 已保存")

# 数据下载配置
st.sidebar.subheader("数据管理")
symbol = st.sidebar.text_input("ETF代码 (如 510300)", "510300")
if st.sidebar.button("下载/更新数据"):
    downloader = DataDownloader()
    with st.spinner(f"正在下载 {symbol} 数据..."):
        df = downloader.download_kline(symbol)
        st.sidebar.success(f"{symbol} 数据更新成功！")

# 加载数据
data_path = f"data/{symbol}.parquet"
if os.path.exists(data_path):
    df = pd.read_parquet(data_path)
    
    # 策略执行
    strategy = MomentumStrategy({"window": window, "threshold": threshold})
    df_with_signals = strategy.generate_signals(df)
    
    # 回测执行
    engine = BacktestEngine(stop_loss_pct=stop_loss)
    results = engine.run(df_with_signals)
    
    # 展示看板
    col1, col2, col3 = st.columns(3)
    
    total_return = (results['equity'].iloc[-1] / results['equity'].iloc[0]) - 1
    max_drawdown = (results['equity'] / results['equity'].cummax() - 1).min()
    
    col1.metric("累计收益率", f"{total_return:.2%}")
    col2.metric("最大回撤", f"{max_drawdown:.2%}")
    col3.metric("当前可用资金", f"{results['equity'].iloc[-1]:.2f}")

    # 图表展示
    st.subheader("净值曲线")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results['date'], y=results['equity'], mode='lines', name='账户净值'))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("最近交易信号")
    signals = results[results['signal'] != 0].tail(10)
    st.table(signals[['date', 'close', 'signal', 'equity']])
    
    # 给出仓位建议
    latest = results.iloc[-1]
    st.info(f"### [信号生成] {latest['date']} \n"
            f"**标的**: {symbol} \n"
            f"**动作**: {'买入' if latest['signal'] == 1 else '卖出' if latest['signal'] == -1 else '观望'} \n"
            f"**建议仓位**: {'100%' if latest['signal'] == 1 else '0%'} \n"
            f"**原因**: 动量突破阈值 {threshold}")

else:
    st.warning("请先在侧边栏输入代码并点击下载数据")

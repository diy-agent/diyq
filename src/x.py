# %%
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("Cell 0: 初始化")
print("=" * 60)

# %%
import xtquant.xtdata as xtdata
client = xtdata.connect()
print(f"[OK] 已连接 MiniQMT")

# 下载板块数据
x=xtdata.get_sector_list()
xtdata.
print(x)

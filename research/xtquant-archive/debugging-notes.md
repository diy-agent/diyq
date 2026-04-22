# XTQuant 调试笔记

从AI Agent对话和实际使用中整理的常见问题及解决方案。

## ❓ xtquant vs miniqmt

### 区别说明

| 特性 | xtquant (新版) | miniqmt (旧版) |
|------|----------------|----------------|
| 安装方式 | `pip install xtquant` | `pip install miniqmt` |
| 安装源 | `https://pypi.thinktrader.net/simple` | PyPI |
| 导入方式 | `from xtquant import xtdata` | `from miniqmt import *` |
| 连接方式 | 自动发现，无需配置 | 需要手动初始化 |
| Python版本 | 3.10~3.12 | 同上 |
| 推荐使用 | ✅ 推荐 | ❌ 已过时 |

### Claude AI对话记录

> **用户**: "你关于 pip install --upgrade miniqmt -i https://pypi.thinktrader.net/simple 的相关参考链接发我，这个页面无法打开"
>
> **说明**: AI Agent最初错误地推荐了miniqmt包名，实际上正确的包名是xtquant，安装源是迅投官方。

> **用户**: "是xtquant吧，为什么你会给miniqmt包"
>
> **说明**: xtquant是迅投QMT官方的Python包名，miniqmt是旧版接口名称。

---

## 🐛 常见错误及解决方案

### 错误1: 模块导入失败

```
ImportError: No module named 'xtquant'
```

**排查步骤**:
1. 确认Python版本: `python --version`（必须在3.10~3.12之间）
2. 确认已安装: `pip list | grep xtquant`
3. 确认安装源正确: `pip install --upgrade xtquant -i https://pypi.thinktrader.net/simple`
4. 如果使用sys.path方式，检查路径是否正确

### 错误2: 行情数据获取失败

```
行情数据为空 / get_latest_quote 返回空dict
```

**排查步骤**:
1. **确认QMT客户端已启动** - 这是最常见的原因
2. 确认已开启MiniQMT模式
3. 检查网络连接
4. 尝试先下载历史数据: `xtdata.download_history_data2(...)`

### 错误3: Windows编码问题

```python
# 修复Windows控制台编码
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```

### 错误4: 连接超时

```
ConnectionTimeout / 连接QMT服务失败
```

**排查步骤**:
1. 检查QMT客户端是否在运行
2. 检查端口是否被占用: `netstat -ano | findstr 58610`
3. 检查防火墙设置
4. 尝试指定端口: `xtdata.set_connect_port(58610)`

### 错误5: Python 3.13+ 不兼容

```
xtquant不支持Python 3.13+
```

**解决方案**:
```bash
# 使用uv管理Python版本
uv python install 3.12
uv venv --python 3.12
```

---

## 🔧 调试技巧

### 1. 连接测试流程

```python
# Step 1: 测试导入
try:
    from xtquant import xtdata
    print("✅ xtquant导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    exit(1)

# Step 2: 测试行情获取
quote = xtdata.get_latest_quote(["600000.SH"])
if quote and "600000.SH" in quote:
    print(f"✅ 行情获取成功: {quote['600000.SH']['lastPrice']}")
else:
    print("❌ 行情获取失败，请确认QMT已启动")
```

### 2. 数据完整性检查

```python
kline = xtdata.get_market_data(
    stock_list=["600000.SH"],
    period="1d",
    start_time="20260401",
    end_time="20260408"
)

if "600000.SH" in kline:
    df = kline["600000.SH"]
    print(f"数据行数: {len(df)}")
    if len(df) == 0:
        print("⚠️ 数据为空，尝试先下载历史数据")
        xtdata.download_history_data2(
            stock_list=["600000.SH"],
            period="1d",
            start_time="20260401",
            end_time="20260408"
        )
```

### 3. 调试命令速查

```bash
# 查看xtquant版本
pip show xtquant

# 检查Python版本
python --version

# 查看已安装的包
pip list | grep xt

# 重新安装
pip uninstall xtquant
pip install xtquant -i https://pypi.thinktrader.net/simple

# 检查QMT端口
netstat -ano | findstr 58610
```

---

## 📊 历史调试记录

### 会话1: OpenCode Agent
- **时间**: 2026-04-08
- **文件**: `~/.local/share/opencode/storage/session_diff/ses_2941c3630ffeh1iUA93Le5gLv5.json`
- **内容**: 创建了test_qmt.py测试脚本，包含xtquant和miniqmt双模式兼容方案

### 会话2: Claude Agent
- **时间**: 2026-04-06
- **会话ID**: `87616e69-6572-4a01-90f7-074d57e000a0`
- **项目**: `C:\Users\Administrator\git\_quant`
- **内容**: 
  - 讨论miniqmt连接方式
  - 纠正了包名错误（miniqmt → xtquant）
  - 讨论了安装源问题

### 会话3: OpenClaw Agent
- **时间**: 2026-04-07~08
- **项目**: `~/.openclaw/workspace/qmt-connector/`
- **内容**: 创建了完整的qmt-connector工具项目
  - 两种连接模式（自动/自定义）
  - CLI命令行工具（基于Cyclopts）
  - 数据获取和保存功能

### 会话4: PowerShell调试历史
- 常用调试命令记录
- uv项目管理相关命令
- qmt-connector项目的实际使用命令

# XTQuant 资料归档

本文档整理了从AI Agent聊天记录、项目代码和调试记录中收集的xtquant/miniqmt相关资料。

## 📁 归档内容

| 文件 | 内容描述 |
|------|----------|
| [setup-guide.md](./setup-guide.md) | 环境配置和安装指南 |
| [api-reference.md](./api-reference.md) | API接口参考和使用示例 |
| [debugging-notes.md](./debugging-notes.md) | 常见问题排查和解决方案 |
| [qmt-connector.md](./qmt-connector.md) | QMT连接器项目完整文档 |
| [agent-conversations.md](./agent-conversations.md) | AI Agent聊天记录整理 |

## 🚀 快速开始

```python
# 方法1: 自动连接（推荐）
from xtquant import xtdata

# 获取实时行情
quote = xtdata.get_latest_quote(["600000.SH", "000001.SZ"])

# 获取K线数据
kline = xtdata.get_market_data(
    stock_list=["600000.SH"],
    period="1d",
    start_time="20260101",
    end_time="20260110"
)
```

## 📌 重要提示

1. **Python版本限制**: xtquant仅支持Python 3.10~3.12，不支持3.13+
2. **QMT客户端**: 必须启动QMT客户端并开启MiniQMT模式
3. **安装源**: 使用官方源 `pip install --upgrade xtquant -i https://pypi.thinktrader.net/simple`

## 📂 源码来源

- `~/.openclaw/workspace/qmt-connector/` - QMT连接器完整项目
- `~/.local/share/opencode/storage/session_diff/` - OpenCode AI对话记录
- `~/.claude/history.jsonl` - Claude AI对话记录
- `~/git/_quant/` - 量化交易项目

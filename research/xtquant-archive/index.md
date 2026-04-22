# XTQuant 资料归档总索引

## 📑 文档列表

### 核心文档

| 文档 | 说明 | 用途 |
|------|------|------|
| [README.md](./README.md) | 归档概述 | 快速了解归档内容 |
| [setup-guide.md](./setup-guide.md) | 环境配置指南 | 首次安装和环境搭建 |
| [api-reference.md](./api-reference.md) | API接口参考 | 开发时查询接口用法 |
| [debugging-notes.md](./debugging-notes.md) | 调试笔记 | 排查问题时参考 |
| [qmt-connector.md](./qmt-connector.md) | QMT连接器项目 | 完整的工具项目文档 |
| [agent-conversations.md](./agent-conversations.md) | AI对话记录 | 了解调试历程 |

## 🎯 快速导航

### 我是新手，想快速开始使用
→ [setup-guide.md](./setup-guide.md)

### 我需要查询API接口用法
→ [api-reference.md](./api-reference.md)

### 我遇到了错误，需要排查
→ [debugging-notes.md](./debugging-notes.md)

### 我想了解完整的工具项目
→ [qmt-connector.md](./qmt-connector.md)

## 📝 关键信息速查

### 安装命令
```bash
pip install --upgrade xtquant -i https://pypi.thinktrader.net/simple
# 或使用uv
uv add xtquant
```

### Python版本要求
```
✅ 3.10, 3.11, 3.12
❌ 3.13+ (不支持)
```

### 最小可用代码
```python
import sys
sys.path.insert(0, "d:/app/qmt/bin.x64")
from xtquant import xtdata

# 获取行情
quote = xtdata.get_latest_quote(["600519.SH"])
print(quote)
```

### CLI工具使用
```bash
# 测试连接
uv run qmt test-connect

# 获取数据
uv run qmt get-data --stocks 600519.SH --start 20240101
```

## 🔍 原始数据来源

所有资料均来自以下AI Agent聊天记录和项目文件：

| 来源 | 路径 | 文件类型 |
|------|------|----------|
| OpenCode | `~/.local/share/opencode/storage/session_diff/` | JSON对话记录 |
| Claude | `~/.claude/history.jsonl` | JSONL对话记录 |
| OpenClaw | `~/.openclaw/workspace/qmt-connector/` | Python项目 |
| Pi | `~/.pi/agent/sessions/` | 会话记录 |
| PowerShell | `~/AppData/Roaming/.../ConsoleHost_history.txt` | 命令历史 |
| Git项目 | `~/git/_quant/` | Markdown文档 |

---

**归档时间**: 2026-04-19  
**归档工具**: Pi Agent

# diyq (diyQuant)

## 项目概览

本项目是一个预测&研究系统，通过金融、股票、新闻的脉略、事件研究，预测所关注内容的发展。

- 数据源: **xtquant** 迅投MiniQMT行情接口 `research\xtquant\xtdata\README.md`
- python: 3.12
- 包管理器: uv

## 开发规范

### sha.sh 使用

```bash
./sha.sh check    # lint + format + type check
./sha.sh test     # 单元测试
./sha.sh sync     # 环境同步
./sha.sh clean    # 清理构建产物
```

### Python 包安装

- **禁止直接使用 `pip install`**，必须使用 `uv add` 或 `uv run`

### 提交规范

- 提交前先 review: `git diff --stat`
- 提交信息遵循 Conventional Commits（`feat:`、`fix:`、`chore:` 等）

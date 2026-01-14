# 量化交易系统 (Lightweight Quantitative Trading System)

基于 Python 3.12 的轻量级量化交易系统。

## 功能特性

- **数据管理**: 使用 AkShare 下载 ETF 日线数据，支持增量下载和 Parquet 格式存储。
- **策略实现**: 内置动量突破策略，支持自定义参数。
- **回测引擎**: 简单的回测逻辑，包含固定比例止损。
- **可视化看板**: 基于 Streamlit 的交互式界面，实时调整参数并查看结果。
- **配置管理**: 支持多策略配置的保存和读取。

## 快速开始

### 1. 环境准备

推荐使用 `uv` 管理依赖：

```bash
uv sync
```

或者使用 `pip`:

```bash
pip install akshare pandas loguru tqdm pyyaml matplotlib streamlit pyarrow fastparquet plotly
```

### 2. 运行系统

```bash
python main.py
```

或者直接运行 Streamlit:

```bash
streamlit run src/ui/app.py
```

## 项目结构

- `data/`: 存储 Parquet 格式的行情数据。
- `configs/`: 存储策略配置 JSON 文件。
- `src/`: 源代码。
  - `data/`: 数据下载模块。
  - `strategy/`: 策略逻辑与回测引擎。
  - `ui/`: Streamlit 可视化界面。
  - `utils/`: 工具类（配置管理等）。
- `main.py`: 项目入口。

## 需求参考

详细需求请参考 [docs/requirements.md](docs/requirements.md)。

技术调研和参考链接 docs/research.md

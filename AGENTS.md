# diyq (diyQuant) — 金融预测与研究

通过股票数据、新闻事件脉络研究，预测关注内容的发展方向。

## 目录结构

| 路径 | 说明 |
|------|------|
| `src/` | Python 源码（data/、strategy/、utils/） |
| `pkgs/diyq-miniqmt/` | MiniQMT 量化包（Python 子包） |
| `main.py` | 入口运行脚本 |
| `env/` | 环境配置 |
| `sha.sh` | 开发入口脚本 |

## 数据源

使用 **xtquant**（迅投 MiniQMT）作为数据源。认证信息在 `env/` 目录下。

## 约束

- 无统一 CLI，运行看 `main.py` 和 `sha.sh` 内容
- 研究性质，结构松散

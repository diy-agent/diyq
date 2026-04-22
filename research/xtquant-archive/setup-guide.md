# XTQuant 环境配置指南

## 1. Python版本要求

```
⚠️ 重要: xtquant仅支持 Python 3.10 ~ 3.12
          不支持 Python 3.13+
```

## 2. 安装方式

### 方式1: 直接安装（推荐）

```bash
# 使用官方源安装
pip install --upgrade xtquant -i https://pypi.thinktrader.net/simple

# 或使用uv
uv add xtquant
```

### 方式2: 通过uv项目管理

```toml
# pyproject.toml
[project]
dependencies = [
    "xtquant>=250516.1.1",
    "pandas >=2.0.0",
    "numpy >=1.24.0",
]
```

```bash
uv sync
```

## 3. QMT客户端配置

### 3.1 前置条件

1. 安装QMT客户端（华鑫/国泰君安/等支持迅投QMT的券商版本）
2. 启动QMT客户端
3. 开启MiniQMT模式

### 3.2 路径配置

```python
import sys

# 将QMT路径添加到Python搜索路径
sys.path.insert(0, "d:/app/qmt/bin.x64")
sys.path.insert(0, "d:/app/qmt/python")
```

### 3.3 连接测试代码

```python
import sys
import io

# 修复Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 优先使用QMT自带的接口
sys.path.insert(0, "d:/app/qmt/bin.x64")
sys.path.insert(0, "d:/app/qmt/python")

try:
    from xtquant import xtdata
    print("✅ 导入xtquant成功，使用新版QMT量化接口")
except ImportError as e:
    print(f"❌ 导入xtquant失败: {e}")
    print("请检查以下几点:")
    print("1. QMT安装路径是否正确（当前配置为d:/app/qmt）")
    print("2. QMT客户端是否已启动，且已开启MiniQMT模式")
    print("3. 确认QMT版本是否支持Python API")
```

## 4. 环境变量配置（可选）

```bash
# Windows PowerShell
$env:QMT_BIN_PATH = "D:\app\qmt\bin.x64"
$env:QMT_PORT = "58610"

# Linux/Mac
export QMT_BIN_PATH="/path/to/qmt/bin.x64"
export QMT_PORT="58610"
```

## 5. 配置文件示例

```toml
# config.toml
[qmt]
# QMT bin.x64目录路径，为空则使用自动连接模式
bin_path = "D:\\app\\qmt\\bin.x64"
port = 58610  # 可选，自定义端口
auto_add_path = true

[output]
format = "json"
save_to_file = false
output_dir = "./data"
```

## 6. 常见问题

### Q1: pip install xtquant 找不到包
**解决方案**: 使用官方源
```bash
pip install --upgrade xtquant -i https://pypi.thinktrader.net/simple
```

### Q2: ImportError: No module named 'xtquant'
**解决方案**: 
1. 确认QMT客户端已启动
2. 检查Python版本是否在3.10~3.12范围内
3. 确认QMT bin路径已添加到sys.path

### Q3: 连接超时
**解决方案**: 
1. 检查QMT客户端是否已启动MiniQMT模式
2. 检查防火墙设置
3. 确认端口未被占用

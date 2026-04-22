import sys
import io

# 修复Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 优先使用QMT自带的接口
sys.path.insert(0, "d:/app/qmt/bin.x64")
sys.path.insert(0, "d:/app/qmt/python")

try:
    from xtquant import xtdata

    print("导入xtquant成功，使用新版QMT量化接口")
    use_xtquant = True
except ImportError as e:
    print(f"导入xtquant失败: {e}，尝试导入旧版miniqmt")
    try:
        from miniqmt import *

        use_xtquant = False
    except ImportError as e:
        print(f"导入miniqmt失败: {e}")
        print("请检查以下几点:")
        print("1. QMT安装路径是否正确（当前配置为d:/app/qmt）")
        print("2. QMT客户端是否已启动，且已开启MiniQMT模式")
        print("3. 确认QMT版本是否支持Python API")
        exit(1)

if __name__ == "__main__":
    if use_xtquant:
        # 新版xtquant接口测试
        print("开始xtquant接口测试...")
        # 测试1: 获取最新行情
        quote = xtdata.get_latest_quote(["600000.SH", "000001.SZ"])
        if "600000.SH" in quote:
            print(f"1. 浦发银行(600000.SH)最新价: {quote['600000.SH']['lastPrice']}")
        else:
            print("1. 浦发银行行情获取失败")

        if "000001.SZ" in quote:
            print(f"   平安银行(000001.SZ)最新价: {quote['000001.SZ']['lastPrice']}")
        else:
            print("   平安银行行情获取失败")

        # 测试2: 获取K线数据
        kline = xtdata.get_market_data(
            stock_list=["600000.SH"],
            period="1d",
            start_time="20260401",
            end_time="20260408",
            fields=["open", "high", "low", "close", "volume"],
        )
        if "600000.SH" in kline:
            df = kline["600000.SH"]
            print(f"2. 浦发银行近7日K线行数: {len(df)}")
            if len(df) > 0:
                latest = df.iloc[-1]
                print(f"   最新收盘价: {latest['close']}, 成交量: {latest['volume']}")

        # 测试3: 获取交易日历
        trade_dates = xtdata.get_trading_dates(
            market="SH", start_time="20260401", end_time="20260410"
        )
        print(
            f"3. 2026年4月上旬交易日数量: {len(trade_dates)}, 日期列表: {trade_dates}"
        )

        print("xtquant接口全部测试通过，QMT量化环境可用")
    else:
        # 旧版miniqmt接口测试
        print("开始miniqmt接口测试...")
        # 初始化MiniQMT客户端
        init_result = init(
            dllpath="d:/app/qmt",
            trade_server_addr="tcp://127.0.0.1:10000",
            is_encrypt=False,
        )

        print(
            f"客户端初始化结果: {'成功' if init_result == 0 else f'失败，错误码: {init_result}'}"
        )
        if init_result != 0:
            exit(1)

        # 测试1: 获取沪市股票列表
        sh_stocks = get_stock_list(market="SH")
        print(f"1. 沪市股票总数: {len(sh_stocks)}, 前5只标的: {sh_stocks[:5]}")

        # 测试2: 获取单只股票实时行情
        quote = get_quote(["600000.SH"])
        print(f"2. 浦发银行(600000.SH)最新行情: {quote.get('600000.SH', {})}")

        # 测试3: 获取交易日历
        trade_dates = get_trade_days(start_date="20260401", end_date="20260410")
        print(f"3. 2026年4月1日-10日交易日: {trade_dates}")

        # 释放客户端资源
        release()
        print("miniqmt接口全部测试通过，QMT量化环境可用")

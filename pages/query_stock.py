import marimo

__generated_with = "0.23.2"
app = marimo.App()

with app.setup:
    import marimo as mo  
    import xtquant.xtdata as xtdata


@app.cell
def _():
    xtdata.connect()
    xtdata.get_sector_list()
    return


@app.cell
def _():
    # 创建多组筛选器  
    categories = ["全部", "电子产品", "服装", "食品"]  
    price_ranges = ["0-100", "100-500", "500-1000", "1000+"]  
    sort_options = ["综合", "价格↑", "价格↓", "销量"]  

    # 状态管理  
    get_cat, set_cat = mo.state("全部")  
    get_price, set_price = mo.state("0-100")   
    get_sort, set_sort = mo.state("综合")  

    # 创建按钮组  
    cat_buttons = mo.ui.array([  
        mo.ui.button(label=c, on_click=lambda v, cat=c: set_cat(cat))   
        for c in categories  
    ])  

    price_buttons = mo.ui.array([  
        mo.ui.button(label=p, on_click=lambda v, price=p: set_price(price))  
        for p in price_ranges  
    ])  

    sort_buttons = mo.ui.array([  
        mo.ui.button(label=s, on_click=lambda v, sort=s: set_sort(sort))  
        for s in sort_options  
    ])  

    # 布局  
    mo.vstack([  
        mo.md("**分类：**") , mo.hstack([cat_buttons], gap=1),  
        mo.md("**价格：**") , mo.hstack([price_buttons], gap=1),   
        mo.md("**排序：**") , mo.hstack([sort_buttons], gap=1)  
    ])  
    return get_cat, get_price, get_sort


@app.cell
def _(get_cat, get_price, get_sort):
    # 显示筛选结果  
    mo.md(f"""  
    ### 筛选条件  
    - 分类：{get_cat()}  
    - 价格：{get_price()}  
    - 排序：{get_sort()}  
    """)  
    return


if __name__ == "__main__":
    app.run()

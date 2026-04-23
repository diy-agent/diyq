import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full", css_file="main.css")

with app.setup:
    import marimo as mo

@app.cell
def _():
    # 创建导航菜单  
    navigation = mo.nav_menu(  
        {  
            "/": f"{mo.icon('lucide:home')} 首页",  
            "/dashboard": f"{mo.icon('lucide:layout-dashboard')} 仪表板",  
            "/analytics": f"{mo.icon('lucide:bar-chart')} 分析",  
            "/settings": f"{mo.icon('lucide:settings')} 设置",  
        },  
        orientation="horizontal"  
    )  
    navigation
    return


@app.cell
def _():
    mo.vstack([  
            mo.md("# 🏠 欢迎来到多页应用"),  
            mo.md("这是主页，使用上方导航在不同页面间切换。")  
        ])  

    return


if __name__ == "__main__":
    app.run()

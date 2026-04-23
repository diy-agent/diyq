import marimo

__generated_with = "0.23.2"
app = marimo.App()

with app.setup:
    import marimo as mo  
    import xtquant.xtdata as xtdata


@app.cell
def _():
    xtdata.get_sector_list()
    return


if __name__ == "__main__":
    app.run()

import asyncio
from nicegui import ui, background_tasks

# 尝试导入 xtdata
from xtquant import xtdata
import asyncio  
from nicegui import ui, background_tasks  
  
progress = ui.linear_progress().props('instant-feedback')  
  
async def download_sector_data():
    print("xxxx")
    xtdata.connect()
    print("xxxx2")
    xtdata.download_sector_data()

def start_process():  
    task = background_tasks.create(download_sector_data())  
    with ui.column() as controls:  
        ui.button('取消任务').on('click', lambda: task.cancel()) .on('click', controls.delete)  

with ui.row():
    ui.button('开始处理', on_click=start_process)

ui.run()
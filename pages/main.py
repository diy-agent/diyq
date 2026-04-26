import aiofiles
import asyncio
from nicegui import background_tasks, ui

results = {'answer': '?'}

async def compute() -> None:
    await asyncio.sleep(1)
    results['answer'] = 42

@background_tasks.await_on_shutdown
async def backup() -> None:
    await asyncio.sleep(1)
    async with aiofiles.open('backup.json', 'w') as f:
        await f.write(f'{results["answer"]}')
    print('backup.json written', flush=True)

ui.label().bind_text_from(results, 'answer', lambda x: f'answer: {x}')
ui.button('Compute', on_click=lambda: background_tasks.create(compute()),)
ui.button('Backup', on_click=lambda: background_tasks.create(backup()))

ui.run()
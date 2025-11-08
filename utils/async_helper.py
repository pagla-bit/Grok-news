# utils/async_helper.py
import asyncio

async def run_single(task_func, arg):
    return await task_func(arg)

def run_async_tasks(task_args, task_func, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_task(arg):
        async with semaphore:
            return await run_single(task_func, arg)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [sem_task(arg) for arg in task_args]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()
    return results

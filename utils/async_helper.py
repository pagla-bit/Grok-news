# utils/async_helper.py
import asyncio

async def _worker(sem, func, arg):
    async with sem:
        return await func(arg)

def run_async_tasks(task_args, task_func, max_concurrent: int = 8):
    sem = asyncio.Semaphore(max_concurrent)

    async def main():
        return await asyncio.gather(*[_worker(sem, task_func, a) for a in task_args])

    return asyncio.run(main())

# utils/async_helper.py
import asyncio

async def _worker(sem, func, arg):
    async with sem:
        return await func(arg)

def run_async_tasks(task_args, task_func, max_concurrent: int = 10):
    """Run many (arg → await task_func(arg)) with limited concurrency."""
    sem = asyncio.Semaphore(max_concurrent)

    async def main():
        return await asyncio.gather(*[_worker(sem, task_func, a) for a in task_args])

    # Streamlit runs in the main thread → create a fresh loop
    return asyncio.run(main())

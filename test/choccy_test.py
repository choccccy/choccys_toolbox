import asyncio

from choccys_toolbox.ui import throbber


async def sleeper(seconds):
    print(f'gonna wait for {seconds} second(s)')
    await asyncio.sleep(seconds)
    print(f'waited for {seconds} second(s)')


async def async_main():
    # collect tasks for concurrent operation
    tasks = [
        asyncio.create_task(sleeper(10)), 
        asyncio.create_task(throbber())
        ]

    # run FIRST task until completed
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
        )


if __name__ == "__main__":
    print()
    asyncio.run(async_main())
    print()
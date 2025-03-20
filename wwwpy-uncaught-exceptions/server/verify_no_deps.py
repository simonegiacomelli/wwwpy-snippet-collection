import asyncio


async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_global_exception_handler)
    asyncio.create_task(_throw_error())


def _global_exception_handler(loop, context):
    print(f'CUSTOM handler caught start')


async def _throw_error():
    print('Throwing error')
    raise ValueError('Verify error handling')


# asyncio.run(main())
await main()

import asyncio


def _set_global_exception_handler():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_global_exception_handler)


def _global_exception_handler(loop, context):
    # The context parameter contains details about the exception
    print(f'CUSTOM handler caught start')
    print(f"CUSTOM handler caught: {context['message']}")
    exception = context.get('exception')
    if exception:
        print(f"Exception type: {type(exception)}, Args: {exception.args}")
        print(exception)


async def _throw_error():
    raise ValueError('Verify error handling')


async def main():
    _set_global_exception_handler()
    asyncio.create_task(_throw_error())


# asyncio.run(main())
await main()

import asyncio
import logging

from wwwpy.common.asynclib import create_task_safe
from wwwpy.common.designer import log_emit

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
log_emit.add_once(print)
logger.info('Logger initialized')


def _set_global_exception_handler():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_global_exception_handler)


def _global_exception_handler(loop, context):
    # The context parameter contains details about the exception
    logger.debug(f'CUSTOM handler caught start')
    logger.info(f"CUSTOM handler caught: {context['message']}")
    exception = context.get('exception')
    if exception:
        logger.info(f"Exception type: {type(exception)}, Args: {exception.args}")
        logger.exception(exception)


async def _throw_error():
    raise ValueError('Verify error handling')


async def main():
    _set_global_exception_handler()
    create_task_safe(_throw_error())


if __name__ == '__main__':
    asyncio.run(main())

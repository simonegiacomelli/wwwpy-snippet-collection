
import logging

logger = logging.getLogger(__name__)

async def echo(msg: str) -> str:
    res = f'echo {msg}'
    logger.debug(f'{res}')
    return res
import inspect
import asyncio

import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.common.asynclib import create_task_safe

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _btn_raise: js.HTMLButtonElement = wpc.element()
    _btn_add_handler: js.HTMLButtonElement = wpc.element()
    _btn_create_task_safe: js.HTMLButtonElement = wpc.element()
    _btn_create_task: js.HTMLButtonElement = wpc.element()
    _btn_add_and_raise: js.HTMLButtonElement = wpc.element()
    _btn_ensure_future: js.HTMLButtonElement = wpc.element()
    taLog: js.HTMLTextAreaElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<button data-name="_btn_raise">_btn_raise</button>
<button data-name="_btn_add_and_raise">_btn_add_and_raise</button>
<button data-name="_btn_add_handler">_btn_add_handler</button>
<button data-name="_btn_create_task_safe">_btn_create_task_safe</button>
<button data-name="_btn_create_task">_btn_create_task</button>
<button data-name="_btn_ensure_future">_btn_ensure_future</button>
<hr>
<textarea data-name="taLog" style='font-size: 0.7em' cols='60' rows='15'></textarea>
"""

    async def after_init_component(self):
        link = 'https://github.com/pyodide/pyodide/issues/4597'
        self._log(f'see issue {link}')
        js.alert(f'see issue {link}')
        logger.debug(f'after_init_component')
        raise Exception('after_init_component')
    def _log(self, msg):
        self.taLog.value += f'{msg}\n'
    async def _btn_raise__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        await self._throw_error()

    async def _btn_add_handler__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_global_exception_handler)

    async def _btn_create_task_safe__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        create_task_safe(self._throw_error())

    async def _throw_error(self):
        print(1 / 0)

    async def _btn_create_task__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        asyncio.create_task(self._throw_error())

    async def _btn_add_and_raise__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        _set_global_exception_handler()

        asyncio.create_task(self._throw_error())

    async def _btn_ensure_future__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        asyncio.ensure_future(self._throw_error())


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

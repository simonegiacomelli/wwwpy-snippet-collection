import inspect
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote.hotkey import hotkey_window

logger = logging.getLogger(__name__)

logging.getLogger('wwwpy.remote.hotkey').setLevel('DEBUG')
_hotkey_window = hotkey_window()
_hotkey_window.enable_log = True

class Component1(wpc.Component, tag_name='component-1'):
    div1: js.HTMLDivElement = wpc.element()
    input1: js.HTMLInputElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div data-name="div1">component-1</div>
<input data-name="input1" placeholder="input1">
"""
        _hotkey_window.add('CTRL-E',self._hotkey_handler)

    def _hotkey_handler(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        return True



# async def div1__keydown(self, event):
    #     logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
    
    # async def input1__keydown(self, event):
    #     logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)

    

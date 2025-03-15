import inspect
import wwwpy.remote.component as wpc
import js

import logging

from remote.uc_toggle_switch import UcToggleSwitchComponent

logger = logging.getLogger(__name__)

class Component1(wpc.Component, tag_name='component-1'):
    input1: js.HTMLInputElement = wpc.element()
    slSwitch1: js.HTMLElement = wpc.element()
    button1: js.HTMLButtonElement = wpc.element()
    sw1: UcToggleSwitchComponent = wpc.element()
    sw2: UcToggleSwitchComponent = wpc.element()
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<hr>
<uc-toggle-switch data-name='sw1' checked text='ccc'></uc-toggle-switch>
<hr>
<div>When a change is applied below, it will be copied to the switch above</div>
<br>
<uc-toggle-switch data-name='sw2' text='changes the above'></uc-toggle-switch>
<hr>
<uc-toggle-switch data-name='sw3' text='This has no event handler'></uc-toggle-switch>
"""
    
    async def sw1__input(self, event):
        logger.debug(f'sw1={self.sw1.checked_bool} ')
        self.sw1.text = f'sw1 checked={self.sw1.checked_bool}'

    async def sw2__input(self, event):
        logger.debug(f'sw2={self.sw1.checked_bool} ')
        self.sw1.checked_bool = self.sw2.checked_bool
        self.sw2.text = f'sw2 checked={self.sw2.checked_bool}'




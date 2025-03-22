from __future__ import annotations
import inspect
import wwwpy.remote.component as wpc
import js

import logging

from remote.dialog_stack import dialog

logger = logging.getLogger(__name__)

class Component1(wpc.Component, tag_name='component-1'):
    _open: js.HTMLButtonElement = wpc.element()
    div1: Component2 = wpc.element()
    select1: js.HTMLSelectElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<button data-name="_open">Open dialog</button>
<hr>

<component-2 data-name="div1"></component-2>
"""
    
    async def _open__click(self, event):
        dialog.open(self.div1.element)




class Component2(wpc.Component, tag_name='component-2'):
    _close: js.HTMLButtonElement = wpc.element()
    def init_component(self):
        # language=html
        self.element.innerHTML = """
 <div>I'm dialog content</div>
    <select data-name="select1">
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
    </select>
<button data-name="_close">Close dialog</button>
"""
    
    async def _close__click(self, event):
        dialog.close(self.element)
    

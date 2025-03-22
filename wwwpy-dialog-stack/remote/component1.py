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
    _result: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<button data-name="_open">Open dialog</button>
<div data-name="_result">Result:</div>

<hr>

<component-2 data-name="div1"></component-2>
"""
    
    async def _open__click(self, event):
        layer = dialog.open(self.div1.element)
        await layer.closure
        self.element.append(layer.guest)
        self._result.innerHTML = f"Result: {layer.closure.result()}"





class Component2(wpc.Component, tag_name='component-2'):
    _title: js.HTMLDivElement = wpc.element()
    _close: js.HTMLButtonElement = wpc.element()
    select1: js.HTMLSelectElement = wpc.element()
    _open_child: js.HTMLButtonElement = wpc.element()
    _child_result: js.HTMLDivElement = wpc.element()
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div data-name="_title">I'm dialog content</div>
    
<button data-name="_open_child">Open child dialog</button>
<div data-name="_child_result">Child result:</div><select data-name="select1">
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
        <option value="option3">Option 3</option>
    </select>
<button data-name="_close">Close dialog</button>
"""
        self._title.innerHTML += f" id={id(self)}"
        self._child = None
    async def _close__click(self, event):
        dialog.close(self.element, self.select1.value)
    
    async def _open_child__click(self, event):
        if self._child is None:
            self._child = Component2()
        result = await dialog.open(self._child.element).closure
        self._child_result.innerHTML = f"Child result: {result}"

    
    

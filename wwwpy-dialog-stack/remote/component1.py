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

<component-2 data-name="div1" style="display: block"></component-2>
"""
    
    async def _open__click(self, event):
        div1 = self.div1
        result = await dialog.open(div1)
        self._result.innerHTML = f"Result: {result}"
        self.element.append(div1.element)





class Component2(wpc.Component, tag_name='component-2'):
    _title: js.HTMLDivElement = wpc.element()
    _close: js.HTMLButtonElement = wpc.element()
    select1: js.HTMLSelectElement = wpc.element()
    _open_child: js.HTMLButtonElement = wpc.element()
    _child_result: js.HTMLDivElement = wpc.element()
    _btn_smaller: js.HTMLButtonElement = wpc.element()
    _btn_bigger: js.HTMLButtonElement = wpc.element()
    span1: js.HTMLSpanElement = wpc.element()
    _width: js.HTMLSpanElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div data-name="_title">I'm dialog content</div>
    
<button data-name="_open_child">Open child dialog</button>
<div data-name="_child_result">Child result:</div>

<button data-name="_btn_smaller">-</button>
<span data-name="_width"></span>
<button data-name="_btn_bigger">+</button>

<select data-name="select1">
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
        result = await dialog.open(self._child)
        self._child_result.innerHTML = f"Child result: {result}"

    def _add(self, delta):
        # Get current width - check if width is already set in style
        current_style_width = self.element.style.width

        if current_style_width and current_style_width.endswith('px'):
            # If width is already set in style, parse it
            current_width = int(float(current_style_width.replace('px', '')))
        else:
            # Otherwise use offsetWidth for initial width
            current_width = self.element.offsetWidth

        # Calculate new width
        new_width = current_width + delta

        # Ensure width doesn't go below a reasonable minimum (e.g., 100px)
        new_width = max(100, new_width)

        # Set the new width
        self.element.style.width = f"{new_width}px"
        self._width.innerHTML = self.element.style.width

    async def _btn_bigger__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        self._add(30)  # Add 30 pixels

    async def _btn_smaller__click(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        self._add(-30)  # Remove 30 pixels


    
    

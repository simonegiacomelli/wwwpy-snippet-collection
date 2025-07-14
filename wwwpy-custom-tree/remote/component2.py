import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)

class Component2(wpc.Component, tag_name='component-2'):
    button1: js.HTMLButtonElement = wpc.element()
    br1: js.HTMLBRElement = wpc.element()
    br2: js.HTMLBRElement = wpc.element()
    br3: js.HTMLBRElement = wpc.element()
    button2: js.HTMLButtonElement = wpc.element()
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-2</div>
<button data-name="button1">
button1</button>
<button data-name="button2">button2</button>
<br>"""

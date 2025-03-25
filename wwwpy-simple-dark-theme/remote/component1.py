import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)

class Component1(wpc.Component, tag_name='component-1'):
    button1: js.HTMLButtonElement = wpc.element()
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<button data-name="button1">button1</button>"""

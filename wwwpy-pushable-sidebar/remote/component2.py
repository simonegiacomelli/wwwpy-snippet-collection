import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)

class Component2(wpc.Component, tag_name='component-2'):
    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-2 without shadow dom</div>"""

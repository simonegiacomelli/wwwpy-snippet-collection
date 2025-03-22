import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _overlay: js.HTMLButtonElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """

<button data-name="_overlay">Overlay spinner for 3 seconds</button>
"""

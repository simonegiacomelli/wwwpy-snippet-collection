import inspect
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
<div>component-1 with shadow dom</div>
"""

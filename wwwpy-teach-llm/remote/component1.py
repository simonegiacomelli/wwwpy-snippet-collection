"""
This component is written to showcase the use of the `wwwpy` library for creating web components.
"""
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    custom_attribute_1: str = wpc.attribute()

    def init_component(self):
        """This method is to be intended as the constructor of the component.
        We cannot use __init__ because there is some dynamic binding between the javascript class instance and
        this class instance. This is also why we can reload the component without reloading the page (notably
        custom elements are do not support undefining them).
        """
        # self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
"""

    async def after_init_component(self):
        """This is called after init_component, it is a convenience method when async initialization is needed."""
        pass

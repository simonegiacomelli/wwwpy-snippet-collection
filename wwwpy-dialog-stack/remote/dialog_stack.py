
from __future__ import annotations
import inspect
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)

class Dialog(wpc.Component, tag_name='dialog-stack'):
    """This represents an overlay, that can support a stack of elements to be shown one at the time."""
    _host: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
    
    <div data-name="_host" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;">
    </div>
"""
        self.stack = []

    def open(self, guest: js.HTMLElement):
        """This should add self.element to the body (if not already added).
        It should first, remove the guest from the body and from the stack.
        Then it should add the guest to the stack and append it to the host.
        """


    def close(self, guest: js.HTMLElement):
        """This should remove the guest from the stack and from the host (if currently in the host).
        If the stack is empty, it should remove self.element from the body.
        """


dialog = Dialog()

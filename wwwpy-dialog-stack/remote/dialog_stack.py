from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


@dataclass
class DialogLayer:
    _parent_dialog: Dialog # this should be a weakref to avoid circular references
    guest: js.HTMLElement
    closure: asyncio.Future = field(default_factory=asyncio.Future)
    """This should be a future that is set when the dialog is closed. The value of the future should be the value passed to the close method."""


    @property
    def component(self) -> wpc.Component | None:
        return wpc.get_component(self.guest)

    def close(self, close_value: any = None):
        """This forwards the close call to the parent_dialog (if still available)."""


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
        self.stack = {}

    def get(self, guest: js.HTMLElement) -> DialogLayer | None:
        """This should return the DialogLayer object for the given guest element.
        If the guest is not in the stack, it should return None.
        """

        return self.stack.get(guest)

    def open(self, guest: js.HTMLElement) -> DialogLayer:
        """This should add self.element to the body (if not already added).
        It should first, remove the guest from the body and from the stack.
        Then it should add the guest to the stack and append it to the host.
        """

    def close(self, guest: js.HTMLElement, close_value: any = None):
        """This should remove the guest from the stack and from the host (if currently in the host).
        If the stack is empty, it should remove self.element from the body.
        It will also set the future to the result of the close_value.
        """


dialog = Dialog()

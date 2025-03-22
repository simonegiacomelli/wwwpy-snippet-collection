from __future__ import annotations

import asyncio
import logging
import weakref
from dataclasses import dataclass, field

import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


@dataclass
class DialogLayer:
    _parent_dialog: weakref.ReferenceType  # Weak reference to avoid circular references
    guest: js.HTMLElement
    closure: asyncio.Future = field(default_factory=asyncio.Future)
    """This should be a future that is set when the dialog is closed. The value of the future should be the value passed to the close method."""

    @property
    def component(self) -> wpc.Component | None:
        return wpc.get_component(self.guest)

    def close(self, close_value: any = None):
        """This forwards the close call to the parent_dialog (if still available)."""
        parent = self._parent_dialog()
        if parent is not None:
            parent.close(self.guest, close_value)


class Dialog(wpc.Component, tag_name='dialog-stack'):
    """This represents an overlay, that can support a stack of elements to be shown one at the time."""
    _host: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
    <style>
    :host {
        display: none;
    }
    
    :host([open]) {
        display: block;
    }
    
    ::slotted(*) {
        padding: 20px;
        border-radius: 8px;
        max-width: 80%;
        max-height: 80%;
        overflow: auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    
    <div data-name="_host" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;">
        <slot></slot>
    </div>
"""
        self.stack = {}
        self.element.style.display = 'none'

    def get(self, guest: js.HTMLElement) -> DialogLayer | None:
        """This should return the DialogLayer object for the given guest element.
        If the guest is not in the stack, it should return None.
        """
        guest_id = guest.id or str(id(guest))
        return self.stack.get(guest_id)

    def open(self, guest: js.HTMLElement) -> DialogLayer:
        """This should add self.element to the body (if not already added).
        It should first, remove the guest from the body and from the stack.
        Then it should add the guest to the stack and append it to the host.
        """
        # Ensure dialog is in the DOM
        if not self.element.isConnected:
            js.document.body.appendChild(self.element)

        # Make dialog visible
        self.element.setAttribute('open', '')
        self.element.style.display = 'block'

        # Create a unique ID for the guest if it doesn't have one
        guest_id = guest.id or str(id(guest))

        # Remove guest from parent if it's in the DOM
        if guest.isConnected and guest.parentElement:
            guest.parentElement.removeChild(guest)

        # Close existing dialog for this guest if it exists
        existing_layer = self.stack.get(guest_id)
        if existing_layer:
            # If the guest is already in a dialog, close it first
            existing_layer.closure.set_result(None)

        # Create new layer
        layer = DialogLayer(
            _parent_dialog=weakref.ref(self),
            guest=guest
        )

        # Add to stack
        self.stack[guest_id] = layer

        # Add guest to host (using slot)
        self.element.appendChild(guest)

        return layer

    def close(self, guest: js.HTMLElement, close_value: any = None):
        """This should remove the guest from the stack and from the host (if currently in the host).
        If the stack is empty, it should remove self.element from the body.
        It will also set the future to the result of the close_value.
        """
        guest_id = guest.id or str(id(guest))
        layer = self.stack.get(guest_id)

        if layer:
            # Remove from stack
            del self.stack[guest_id]

            # Remove from host if it's a child of the dialog
            if guest.isConnected and guest.parentElement == self.element:
                self.element.removeChild(guest)

            # Complete the future with the close value
            if not layer.closure.done():
                layer.closure.set_result(close_value)

        # If stack is empty, hide dialog
        if not self.stack:
            self.element.removeAttribute('open')
            self.element.style.display = 'none'

            # Optionally remove from DOM
            # if self.element.isConnected:
            #     js.document.body.removeChild(self.element)


# Global dialog instance
dialog = Dialog()
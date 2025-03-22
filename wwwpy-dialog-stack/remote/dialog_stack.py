from __future__ import annotations

import asyncio
import logging
import weakref
from dataclasses import dataclass, field
from typing import Optional, List

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

    def open(self) -> Optional[DialogLayer]:
        """This forwards the open call to the parent_dialog (if still available)."""
        parent = self._parent_dialog()
        if parent is not None:
            return parent.open(self.guest)
        return None


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
            border: 2px solid rgba(255, 255, 255, 0.5);
            background-color: rgba(30, 30, 30, 0.95);
            color: #e0e0e0;
        }
    </style>
    
    <div data-name="_host"
         style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;">
        <slot></slot>
    </div>
"""
        # Dictionary to store all layers by guest ID, also maintains stack order (Python 3.7+)
        self.layers = {}

        self.element.style.display = 'none'

    def _ensure_dialog_visible(self):
        """Helper method to ensure dialog is in DOM and visible"""
        if not self.element.isConnected:
            js.document.body.appendChild(self.element)
        self.element.setAttribute('open', '')
        self.element.style.display = 'block'

    def _get_guest_id(self, guest: js.HTMLElement) -> str:
        """Helper method to get or create a unique ID for a guest element"""
        return guest.id or str(id(guest))

    def _detach_guest(self, guest: js.HTMLElement):
        """Helper method to detach a guest from its parent if connected"""
        if guest.isConnected and guest.parentElement:
            guest.parentElement.removeChild(guest)

    def _show_guest(self, guest: js.HTMLElement):
        """Helper method to add a guest to the host"""
        self._ensure_dialog_visible()
        self.element.appendChild(guest)

    def _hide_guest(self, guest: js.HTMLElement):
        """Helper method to remove a guest from the host"""
        if guest.isConnected and guest.parentElement == self.element:
            self.element.removeChild(guest)

    def _get_top_guest_id(self) -> str | None:
        """Helper method to get the ID of the top dialog in the stack"""
        if not self.layers:
            return None
        return next(reversed(self.layers.keys()))

    def _get_top_layer(self) -> DialogLayer | None:
        """Helper method to get the top layer in the stack"""
        top_id = self._get_top_guest_id()
        return self.layers.get(top_id) if top_id else None

    def get(self, guest: js.HTMLElement) -> DialogLayer | None:
        """Returns the DialogLayer object for the given guest element.
        If the guest is not in the stack, it returns None.
        """
        guest_id = self._get_guest_id(guest)
        return self.layers.get(guest_id)

    def get_or_create(self, guest: js.HTMLElement) -> DialogLayer:
        """Creates a new DialogLayer for the given guest element.
        It adds the guest to the layers dict but not to the host or active stack.
        If a DialogLayer already exists for the guest, it returns that one instead.
        """
        guest_id = self._get_guest_id(guest)

        # Check if a layer already exists for this guest
        existing_layer = self.layers.get(guest_id)
        if existing_layer:
            # Reset the future if it was already completed
            if existing_layer.closure.done():
                existing_layer.closure = asyncio.Future()
            return existing_layer

        # Create new layer
        layer = DialogLayer(
            _parent_dialog=weakref.ref(self),
            guest=guest
        )

        # Add to layers dictionary
        self.layers[guest_id] = layer

        return layer

    def open(self, guest: js.HTMLElement) -> asyncio.Future:
        """Adds a new dialog to the stack and displays it.
        If there is a currently active dialog, it will be hidden but kept in the stack.
        """
        # Detach guest from its current parent
        self._detach_guest(guest)

        # Get the guest ID
        guest_id = self._get_guest_id(guest)

        # Hide current top dialog if it exists and is different from the one we're opening
        top_layer = self._get_top_layer()
        if top_layer and self._get_guest_id(top_layer.guest) != guest_id:
            self._hide_guest(top_layer.guest)

        # If this guest is already in the stack, remove it to reinsert at the top
        if guest_id in self.layers:
            # Store the layer before removing
            layer = self.layers[guest_id]
            # Remove from the dict
            del self.layers[guest_id]
        else:
            # Create new layer if not already in stack
            layer = self.get_or_create(guest)

        # Re-add to layers dict to move it to the end (top of stack)
        self.layers[guest_id] = layer

        # Make dialog visible and show the guest
        self._show_guest(guest)

        return layer.closure

    def close(self, guest: js.HTMLElement, close_value: any = None):
        """Removes a dialog from the stack and shows the previous one if available.
        Resolves the closure future with the close_value.
        """
        guest_id = self._get_guest_id(guest)
        layer = self.layers.get(guest_id)

        if layer:
            # Hide the guest
            self._hide_guest(guest)

            # Remove from layers dictionary (removing from stack)
            del self.layers[guest_id]

            # Complete the future with the close value
            if not layer.closure.done():
                layer.closure.set_result(close_value)

            # Show the previous dialog in the stack if there is one
            top_layer = self._get_top_layer()
            if top_layer:
                self._show_guest(top_layer.guest)
            else:
                # If stack is empty, hide dialog
                self.element.removeAttribute('open')
                self.element.style.display = 'none'


# Global dialog instance
dialog = Dialog()
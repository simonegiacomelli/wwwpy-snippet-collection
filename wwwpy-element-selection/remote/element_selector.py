from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging

logger = logging.getLogger(__name__)


class ElementSelector(wpc.Component, tag_name='element-selector'):
    highlight_element: js.HTMLDivElement = wpc.element()
    toolbar_element: js.HTMLDivElement = wpc.element()

    def init_component(self):
        """Initialize the ElementSelector component"""
        # Create a shadow DOM
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # Create the template with HTML structure
        self.element.shadowRoot.innerHTML = """
            <style>
                :host {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 100;
                }

                .highlight-overlay {
                    position: fixed;
                    pointer-events: none;
                    border: 2px solid #4a90e2;
                    background-color: rgba(74, 144, 226, 0.1);
                    z-index: 100;
                    transition: all 0.2s ease;
                    display: none;
                }

                .toolbar {
                    position: fixed;
                    display: none;
                    background-color: #333;
                    border-radius: 4px;
                    padding: 4px;
                    z-index: 101;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    white-space: nowrap;
                    min-width: max-content;
                    pointer-events: auto;
                }

                .toolbar button {
                    background-color: transparent;
                    color: white;
                    border: none;
                    width: 30px;
                    height: 30px;
                    border-radius: 3px;
                    cursor: pointer;
                    margin: 0 2px;
                }

                .toolbar button:hover {
                    background-color: rgba(255,255,255,0.2);
                }
            </style>
            <div class="highlight-overlay" data-name="highlight_element"></div>
            <div class="toolbar" role="toolbar" aria-label="Element actions" data-name="toolbar_element"></div>
        """

        # Initialize properties
        self._selected_element = None
        self._toolbar_dimensions = None
        self._raf_id = None

        # Create toolbar buttons
        button_data = [
            {"label": "Move up", "icon": "↑"},
            {"label": "Move down", "icon": "↓"},
            {"label": "Edit", "icon": "✏️"},
            {"label": "Delete", "icon": "🗑️"}
        ]

        for data in button_data:
            button = js.document.createElement("button")
            button.setAttribute("aria-label", data["label"])
            button.setAttribute("title", data["label"])
            button.textContent = data["icon"]

            # Using create_proxy to ensure 'this' refers to the right context
            button.addEventListener("click", create_proxy(
                lambda e, action=data["label"]: self._handle_button_click(e, action)
            ))

            self.toolbar_element.appendChild(button)

    def _handle_button_click(self, e, action):
        """Handle toolbar button clicks"""
        e.stopPropagation()
        # Dispatch a custom event when a toolbar button is clicked
        self.element.dispatchEvent(
            js.CustomEvent.new(
                "toolbar-action",
                dict_to_js({
                    "bubbles": True,
                    "composed": True,
                    "detail": {
                        "action": action,
                        "element": self._selected_element
                    }
                })
            )
        )

    def connectedCallback(self):
        """Called when the element is added to the DOM"""
        # Add event listeners
        js.window.addEventListener("resize", create_proxy(self.handle_resize))
        js.window.addEventListener("scroll", create_proxy(self.handle_scroll), dict_to_js({"passive": True}))

    def disconnectedCallback(self):
        """Called when the element is removed from the DOM"""
        # Clean up event listeners
        js.window.removeEventListener("resize", create_proxy(self.handle_resize))
        js.window.removeEventListener("scroll", create_proxy(self.handle_scroll))

        # Cancel any pending animation frame
        if self._raf_id is not None:
            js.window.cancelAnimationFrame(self._raf_id)
            self._raf_id = None

    @property
    def selected_element(self):
        """Get the currently selected element"""
        return self._selected_element

    @selected_element.setter
    def selected_element(self, element):
        """Set the selected element and update the highlight"""
        self._selected_element = element
        self.update_highlight()

    def update_highlight(self):
        """Update the highlight position based on the selected element"""
        if not self._selected_element:
            self.highlight_element.style.display = "none"
            self.toolbar_element.style.display = "none"
            return

        rect = self._selected_element.getBoundingClientRect()

        # Position the highlight overlay using fixed positioning
        self.highlight_element.style.display = "block"
        self.highlight_element.style.top = f"{rect.top}px"
        self.highlight_element.style.left = f"{rect.left}px"
        self.highlight_element.style.width = f"{rect.width}px"
        self.highlight_element.style.height = f"{rect.height}px"

        self.update_toolbar_position(rect)

    def update_toolbar_position(self, rect):
        """Update the toolbar position based on the element position"""
        # Only measure the toolbar once initially to avoid layout thrashing
        if not self._toolbar_dimensions:
            self.toolbar_element.style.display = "block"
            self.toolbar_element.style.visibility = "hidden"
            self.toolbar_element.style.top = "-9999px"  # Position off-screen for measurement

            # Cache toolbar dimensions
            self._toolbar_dimensions = {
                "width": self.toolbar_element.offsetWidth,
                "height": self.toolbar_element.offsetHeight
            }

        # Use cached dimensions
        toolbar_width = self._toolbar_dimensions["width"]
        toolbar_height = self._toolbar_dimensions["height"]

        # Position the toolbar at bottom-right
        toolbar_x = rect.right - toolbar_width  # Align right edges
        toolbar_y = rect.bottom + 5  # Add 5px offset

        # Check if the toolbar would go off-screen to the left
        if toolbar_x < 0:
            toolbar_x = rect.left

        # Check if toolbar would go off-screen at the bottom
        if rect.bottom + toolbar_height + 5 > js.window.innerHeight:
            toolbar_y = rect.top - toolbar_height - 5

        self.toolbar_element.style.display = "block"
        self.toolbar_element.style.visibility = "visible"
        self.toolbar_element.style.left = f"{toolbar_x}px"
        self.toolbar_element.style.top = f"{toolbar_y}px"

    def handle_resize(self, event=None):
        """Handle window resize events"""
        # Clear cached toolbar dimensions on resize
        self._toolbar_dimensions = None

        if self._selected_element:
            self.update_highlight()

    def handle_scroll(self, event=None):
        """Handle window scroll events"""
        # Skip scroll updates if the element isn't selected
        if not self._selected_element:
            return

        # Use requestAnimationFrame to ensure smooth updates
        if self._raf_id is not None:
            js.window.cancelAnimationFrame(self._raf_id)

        self._raf_id = js.window.requestAnimationFrame(create_proxy(lambda _: self._update_on_scroll()))

    def _update_on_scroll(self):
        """Update the highlight after a scroll event"""
        self.update_highlight()
        self._raf_id = None
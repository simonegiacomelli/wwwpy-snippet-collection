from __future__ import annotations

import logging
from collections.abc import Callable

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class ElementSelector(wpc.Component, tag_name='element-selector'):
    """A component for selecting, highlighting, and providing a toolbar for elements.
    Converted from the JavaScript implementation in selection-scroll-1.html.
    """

    # Elements to track
    highlight_overlay: HighlightOverlay = wpc.element()
    toolbar_element: js.HTMLDivElement = wpc.element()

    def init_component(self):
        """Initialize the component"""
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # language=html
        self.element.shadowRoot.innerHTML = """
        <style>
            :host {
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              pointer-events: none;
              z-index: 200000;
            }

            .toolbar {
              position: fixed;
              display: none;
              background-color: #333;
              border-radius: 4px;
              padding: 4px;
              z-index: 200001;
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
        <highlight-overlay data-name="highlight_overlay"></highlight-overlay>
        <div class="toolbar" role="toolbar" aria-label="Element actions" data-name="toolbar_element"></div>
        """
        self.highlight_element = self.highlight_overlay.overlay
        # self.highlight_element = highlight_overlay
        # Initialize properties
        self._selected_element = None
        self._toolbar_dimensions = None
        self._raf_id = None

        # Create toolbar buttons
        button_data = [
            {'label': 'Parent', 'icon': '←'},
            {'label': 'Move up', 'icon': '↑'},
            {'label': 'Move down', 'icon': '↓'},
            {'label': 'Edit', 'icon': '✏️'},
            {'label': 'Delete', 'icon': '🗑️'}
        ]

        for data in button_data:
            button = js.document.createElement('button')
            button.setAttribute('aria-label', data['label'])
            button.setAttribute('title', data['label'])
            button.textContent = data['icon']

            # Create a proxy function to handle the click event
            def create_button_click_handler(action_label):
                def button_click_handler(e):
                    e.stopPropagation()
                    # Dispatch a custom event when a toolbar button is clicked
                    self.element.dispatchEvent(
                        js.CustomEvent.new('toolbar-action', dict_to_js({
                            'bubbles': True,
                            'composed': True,
                            'detail': {
                                'action': action_label,
                                'element': self._selected_element
                            }
                        }))
                    )

                return button_click_handler

            # Add event listener with the proxy function
            button.addEventListener('click', create_proxy(create_button_click_handler(data['label'])))
            self.toolbar_element.appendChild(button)

            self._window_monitor = WindowMonitor(lambda: self._selected_element is not None)
            self._window_monitor.listeners.append(lambda: self.update_highlight())

    def connectedCallback(self):
        self._window_monitor.install()

    def disconnectedCallback(self):
        self._window_monitor.uninstall()

    def set_selected_element(self, element):
        """Set the selected element and update the highlight and toolbar"""
        if self._selected_element == element:
            return
        self._selected_element = element
        self.update_highlight()

    def get_selected_element(self):
        """Get the currently selected element"""
        return self._selected_element

    def update_highlight(self):
        """Update the position and visibility of the highlight overlay and toolbar"""
        if not self._selected_element:
            self.highlight_element.style.display = 'none'
            self.toolbar_element.style.display = 'none'
            return

        # Get the bounding rectangle of the selected element
        rect = self._selected_element.getBoundingClientRect()

        # Position the highlight overlay
        self.highlight_element.style.display = 'block'
        self.highlight_element.style.top = f"{rect.top}px"
        self.highlight_element.style.left = f"{rect.left}px"
        self.highlight_element.style.width = f"{rect.width}px"
        self.highlight_element.style.height = f"{rect.height}px"

        # Update the toolbar position
        self.update_toolbar_position(rect)

    def update_toolbar_position(self, rect):
        """Update the position of the toolbar"""
        # Only measure the toolbar once initially to avoid layout thrashing
        if not self._toolbar_dimensions:
            self.toolbar_element.style.display = 'block'
            self.toolbar_element.style.visibility = 'hidden'
            self.toolbar_element.style.top = '-9999px'  # Position off-screen for measurement

            # Cache toolbar dimensions
            self._toolbar_dimensions = {
                'width': self.toolbar_element.offsetWidth,
                'height': self.toolbar_element.offsetHeight
            }

        # Use cached dimensions
        toolbar_width = self._toolbar_dimensions['width']
        toolbar_height = self._toolbar_dimensions['height']

        # Position the toolbar at bottom-right
        toolbar_x = rect.right - toolbar_width  # Align right edges
        toolbar_y = rect.bottom + 5  # Add 5px offset

        # Check if the toolbar would go off-screen to the left
        if toolbar_x < 0:
            toolbar_x = rect.left

        # Check if toolbar would go off-screen at the bottom
        if rect.bottom + toolbar_height + 5 > js.window.innerHeight:
            toolbar_y = rect.top - toolbar_height - 5

        self.toolbar_element.style.display = 'block'
        self.toolbar_element.style.visibility = 'visible'
        self.toolbar_element.style.left = f"{toolbar_x}px"
        self.toolbar_element.style.top = f"{toolbar_y}px"


class WindowMonitor:

    def __init__(self, enable_notify: callable):
        self._enable_notify = enable_notify
        self.listeners: list[Callable] = []
        self._raf_id = None

    def install(self):
        js.window.addEventListener('resize', create_proxy(self._handle_event))
        js.window.addEventListener('scroll', create_proxy(self._handle_event), dict_to_js({'passive': True}))

    def uninstall(self):
        js.window.removeEventListener('resize', create_proxy(self._handle_event))
        js.window.removeEventListener('scroll', create_proxy(self._handle_event))

        # Cancel any pending animation frame
        if self._raf_id is not None:
            js.window.cancelAnimationFrame(self._raf_id)
            self._raf_id = None

    async def _handle_event(self, event=None):
        if not self._enable_notify():
            return

        # Use requestAnimationFrame to ensure smooth updates
        if self._raf_id is not None:
            js.window.cancelAnimationFrame(self._raf_id)

        def update_on_animation_frame(event):
            self._fire_notify()
            self._raf_id = None

        self._raf_id = js.window.requestAnimationFrame(create_proxy(update_on_animation_frame))

    def _fire_notify(self):
        if not self._enable_notify():
            return
        for listener in self.listeners:
            try:
                listener()
            except Exception as e:
                logger.error(f"Error in listener: {e}")


class HighlightOverlay(wpc.Component, tag_name='highlight-overlay'):
    overlay: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <style>
            .highlight-overlay {
             position: fixed;
              pointer-events: none;
              border: 2px solid #4a90e2;
              background-color: rgba(74, 144, 226, 0.1);
              z-index: 200000;
              transition: all 0.2s ease;
              display: none;
            }
        </style>      
        <div class="highlight-overlay" data-name="overlay"></div>
        """

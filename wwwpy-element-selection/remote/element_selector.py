from __future__ import annotations

import logging
from collections.abc import Callable

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class ElementSelector(wpc.Component, tag_name='element-selector'):
    highlight_overlay: HighlightOverlay = wpc.element()
    toolbar_button: ToolbarButton = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # language=html
        self.element.shadowRoot.innerHTML = """
        <highlight-overlay data-name="highlight_overlay"></highlight-overlay>
        <toolbar-button data-name="toolbar_button"></toolbar-button>
        """
        self.toolbar_element = self.toolbar_button.element
        self._selected_element: js.HTMLElement | None = None
        self._toolbar_dimensions = None
        self._raf_id = None

        self._window_monitor = WindowMonitor(lambda: self._selected_element is not None)
        self._window_monitor.listeners.append(lambda: self.update_highlight_no_transitions())
        self.highlight_overlay.transition = True

    def connectedCallback(self):
        self._window_monitor.install()

    def disconnectedCallback(self):
        self._window_monitor.uninstall()

    def set_selected_element(self, element):
        if self._selected_element == element:
            return
        self._selected_element = element
        self.update_highlight()

    def get_selected_element(self):
        return self._selected_element

    def update_highlight_no_transitions(self):
        self.highlight_overlay.transition = False
        self.update_highlight()
        self.highlight_overlay.transition = True

    def update_highlight(self):
        if not self._selected_element:
            self.highlight_overlay.hide()
            self.toolbar_button.hide()
            return

        rect = self._selected_element.getBoundingClientRect()

        self.highlight_overlay.show(rect)
        self.toolbar_button.show(rect)


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

        if self._raf_id is not None:
            js.window.cancelAnimationFrame(self._raf_id)
            self._raf_id = None

    async def _handle_event(self, event=None):
        if not self._enable_notify():
            return

        self._fire_notify()
        # if self._raf_id is not None:
        #     js.window.cancelAnimationFrame(self._raf_id)

        # def update_on_animation_frame(event):
        #     self._fire_notify()
        #     self._raf_id = None

        # self._raf_id = js.window.requestAnimationFrame(create_proxy(update_on_animation_frame))

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
            .no-transition {
              position: fixed;
              pointer-events: none;
              border: 2px solid #4a90e2;
              background-color: rgba(74, 144, 226, 0.1);
              z-index: 200000;
              display: none;
            } 
            
            .transition {
              transition: all 0.2s ease; 
            }
        </style>      
        <div class="no-transition" data-name="overlay"></div>
        """

    @property
    def transition(self) -> bool:
        return self.overlay.classList.contains('transition')

    @transition.setter
    def transition(self, value: bool):
        if value:
            self.overlay.classList.add('transition')
            # self.overlay.classList.remove('no-transition')
        else:
            self.overlay.classList.remove('transition')
            # self.overlay.classList.add('no-transition')

    def hide(self):
        self.overlay.style.display = 'none'

    def show(self, rect: js.DOMRect):
        self.overlay.style.display = 'block'
        self.overlay.style.top = f"{rect.top}px"
        self.overlay.style.left = f"{rect.left}px"
        self.overlay.style.width = f"{rect.width}px"
        self.overlay.style.height = f"{rect.height}px"


# this class is an extraction  of the toolbar above (refactoring)
class ToolbarButton(wpc.Component, tag_name='toolbar-button'):
    """A component for creating a toolbar button with an icon and label.
    Converted from the JavaScript implementation in selection-scroll-1.html.
    """

    def init_component(self):
        """Initialize the component"""
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
        <style>
             :host {
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

            button {
              background-color: transparent;
              color: white;
              border: none;
              width: 30px;
              height: 30px;
              border-radius: 3px;
              cursor: pointer;
              margin: 0 2px;
            }

            button:hover {
              background-color: rgba(255,255,255,0.2);
            }
        </style>
        <button data-name="button1">←</button>
        <button data-name="button2">↑</button>
        """
        self._toolbar_dimensions = None
        self.toolbar_element = self.element
        self.element.addEventListener('click', create_proxy(self._handle_click))

    def _handle_click(self, event):
        event.stopPropagation()

    def hide(self):
        self.element.style.display = 'none'

    def show(self, rect):
        # self._toolbar_dimensions = None
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

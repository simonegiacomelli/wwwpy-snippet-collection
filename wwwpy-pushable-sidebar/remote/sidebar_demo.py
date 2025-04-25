from __future__ import annotations

import asyncio
import datetime
import logging

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer import element_path
from wwwpy.remote.designer.helpers import _element_path_lbl
from wwwpy.remote.designer.ui import palette  # noqa
from wwwpy.remote.designer.ui.element_selector import ElementSelector
from wwwpy.remote.designer.ui.property_editor import _rebase_element_path_to_origin_source
from wwwpy.remote.jslib import is_contained, get_deepest_element

from . import pushable_sidebar  # Import the PushableSidebar component

logger = logging.getLogger(__name__)


class SidebarDemo(wpc.Component, tag_name='sidebar-demo'):
    # Element references using wpc.element()
    toggle_button: js.HTMLButtonElement = wpc.element()
    add_content_button: js.HTMLButtonElement = wpc.element()
    state_select: js.HTMLSelectElement = wpc.element()
    position_select: js.HTMLSelectElement = wpc.element()
    width_input: js.HTMLInputElement = wpc.element()
    apply_width_button: js.HTMLButtonElement = wpc.element()
    sidebar: pushable_sidebar.PushableSidebar = wpc.element()  # Reference to the sidebar component
    _palette: palette.PaletteComponent = wpc.element()  # Reference to the palette component
    element_selector: ElementSelector = wpc.element()
    _lbl1: js.HTMLDivElement = wpc.element()
    _lbl2: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # Create shadow DOM for style isolation
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # Define component HTML structure with shadow DOM
        # language=html
        self.element.shadowRoot.innerHTML = """
                                            <style>
                                                /* Component styles */
                                                :host {
                                                    display: block;
                                                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                                }

                                                .content {
                                                    padding: 20px;
                                                    max-width: 1200px;
                                                    margin: 0 auto;
                                                }

                                                h1 {
                                                    color: white;
                                                    border-bottom: 1px solid #eee;
                                                    padding-bottom: 10px;
                                                }

                                                .controls {
                                                    margin: 20px 0;
                                                    padding: 20px;
                                                    background-color: #f5f5f5;
                                                    border-radius: 5px;
                                                }

                                                button {
                                                    padding: 8px 16px;
                                                    margin: 5px;
                                                    background-color: #4CAF50;
                                                    color: white;
                                                    border: none;
                                                    border-radius: 4px;
                                                    cursor: pointer;
                                                }

                                                button:hover {
                                                    background-color: #45a049;
                                                }

                                                select, input {
                                                    padding: 8px;
                                                    margin: 5px;
                                                    border: 1px solid #ddd;
                                                    border-radius: 4px;
                                                }

                                                /* Style for the body through a global style */
                                                :host {
                                                    --sidebar-transition: padding 0.3s ease;
                                                }
                                            </style>
                                            <element-selector data-name="element_selector"
                                                              id="element-selector"></element-selector>

                                            <pushable-sidebar data-name="sidebar" position="left" width="300px">
                                                <div class="sidebar-content">
                                                    <h3>Pushable Sidebar</h3>
                                                    <p>This is a sidebar that doesn't overlap content.</p>

                                                    <h4>Menu</h4>
                                                    <wwwpy-palette data-name="_palette"></wwwpy-palette>
                                                    <ul class="sidebar-menu">
                                                        <li>Dashboard</li>
                                                        <li>Profile</li>
                                                        <li>Settings</li>
                                                        <li>Notifications</li>
                                                        <li>Help</li>
                                                    </ul>
                                                </div>
                                                <div data-name="_lbl1">hello</div>
                                                <div data-name="_lbl2">hello</div>
                                            </pushable-sidebar>

                                            <!-- Main content -->
                                            <div class="content">
                                                <h1>Demo Mixer</h1>

                                                <p>This demo shows how to use the PushableSidebar library to create
                                                    sidebars that push content away instead of overlapping it.</p>

                                                <div class="controls">
                                                    <h3>Control Panel</h3>
                                                    <button data-name="toggle_button">Toggle Sidebar State</button>
                                                    <button data-name="add_content_button">Add Content</button>

                                                    <div style="margin-top: 15px;">
                                                        <label>State:
                                                            <select data-name="state_select">
                                                                <option value="expanded">Expanded</option>
                                                                <option value="collapsed">Collapsed</option>
                                                                <option value="hidden">Hidden</option>
                                                            </select>
                                                        </label>

                                                        <label style="margin-left: 15px;">
                                                            Position:
                                                            <select data-name="position_select">
                                                                <option value="left">Left</option>
                                                                <option value="right">Right</option>
                                                            </select>
                                                        </label>

                                                        <label style="margin-left: 15px;">
                                                            Width:
                                                            <input type="text" data-name="width_input" value="300px">
                                                            <button data-name="apply_width_button">Apply</button>
                                                        </label>
                                                    </div>
                                                </div>
                                            </div> \
                                            """

        self._add_global_styles()
        self._action_manager = self._palette.action_manager
        self._palette.add_item('item1', 'Item 1')
        self._palette.add_item('item2', 'Item 2')
        self._palette.add_item('item3', 'Item 3')
        self._palette.add_item('item4', 'Item 4')

        self._action_manager.listeners_for(palette.HoverEvent).add(self._hover_handler)
        self._action_manager.listeners_for(palette.AcceptEvent).add(self._accept_handler)
        self._update_lbl = 0

    def _add_global_styles(self):
        style = js.document.createElement('style')
        style.textContent = _style
        self._style_element = style
        js.document.head.appendChild(style)

    async def after_init_component(self):
        # Set up event listener for sidebar state changes
        # This is needed for external events not handled by the auto-binding mechanism
        self.sidebar.element.addEventListener(
            'sidebar-state-change',
            create_proxy(self.handle_sidebar_state_change)
        )

    def connectedCallback(self):
        f"""Called when the element is added to the DOM"""

    def disconnectedCallback(self):
        # Remove the global styles when component is disconnected
        if hasattr(self, '_style_element') and js.document.head.contains(self._style_element):
            js.document.head.removeChild(self._style_element)

    async def toggle_button__click(self, event):
        self.sidebar.toggle()
        self._log(f"Sidebar toggled to state: {self.sidebar.get_state()}")

    async def add_content_button__click(self, event):
        div = js.document.createElement('div')
        time_str = js.Date.new().toLocaleTimeString()
        div.textContent = f'New content added at {time_str}'
        div.style.padding = '10px'
        div.style.margin = '10px 0'
        div.style.backgroundColor = 'rgba(255,255,255,0.1)'
        div.style.borderRadius = '4px'

        self.sidebar.element.appendChild(div)
        self._log(f"Content added at {time_str}")

    async def state_select__change(self, event):
        new_state = self.state_select.value
        self.sidebar.set_state(new_state)
        self._log(f"State changed to: {new_state}")

    async def position_select__change(self, event):
        new_position = self.position_select.value
        self.sidebar.set_position(new_position)
        self._log(f"Position changed to: {new_position}")

    async def apply_width_button__click(self, event):
        width = self.width_input.value
        self.sidebar.set_width(width)
        self._log(f"Width changed to: {width}")

    async def sidebar__sidebar_state_change(self, event):
        new_state = event.detail.newState
        self.state_select.value = new_state
        self._log(f"Sidebar state changed to: {new_state}")

    def handle_sidebar_state_change(self, event):
        new_state = event.detail.newState
        self.state_select.value = new_state

    def _log(self, message: str):
        now = datetime.datetime.now()
        logger.info(f"{now} - {message}")

    def _hover_handler(self, hover_event: palette.HoverEvent):
        event = hover_event.js_event
        self._update_selected_action_label()
        if not self._action_manager.selected_action:
            return
        self._set_selection_from_js_event(event)

    def _accept_handler(self, accept_event: palette.AcceptEvent):
        logger.debug(f'accept_handler: {accept_event}')
        if self._action_manager.selected_action is None:
            return
        self._set_selection_from_js_event(accept_event.js_event)
        self._update_selected_action_label()
        accept_event.accept()

    def _update_selected_action_label(self):
        self._update_lbl += 1
        self._lbl2.innerHTML = f'update {self._update_lbl}'

        sa = self._action_manager.selected_action
        sel_label = 'None' if sa is None else sa.label
        msg = f'palette item selected: {sel_label}'
        if msg == self._lbl1.innerHTML:
            return
        logger.debug(msg)
        self._lbl1.innerHTML = msg

    def _set_selection_from_js_event(self, event):
        # path = event.composedPath()
        # composed = path and len(path) > 0
        composed = 'disabled'
        # target = path[0] if composed else event.target
        target = _element_from_js_event(event)

        if not self.element_selector.is_selectable(target):
            target = None
        unselectable = is_contained(target, self._palette.element)
        if unselectable or target == js.document.body or target == js.document.documentElement:
            target = None

        if self.element_selector.get_selected_element() == target:
            return
        logger.debug(f'set_selection: {_pretty(target)}, unselectable: {unselectable}, composed: {composed}')
        js.console.log('set_selection console', event, event.composedPath())
        self.element_selector.set_selected_element(target)
        self._next_element = target

        async def more_snappy():
            await asyncio.sleep(0.2)
            if self._next_element != target:
                logger.debug(f'more_snappy: element changed, skipping')
                return
            ep_live = element_path.element_path(target)
            logger.debug(f'Element path live: {ep_live}')
            ep_source = _rebase_element_path_to_origin_source(ep_live)
            logger.debug(f'Element path source: {ep_source}')
            message = 'ep_source is none' if ep_source is None else f'ep_source: {_element_path_lbl(ep_source)}'
            logger.debug(message)
            if ep_source is not None:
                from wwwpy.remote.designer.ui.dev_mode_component import DevModeComponent
                tb = DevModeComponent.instance.toolbox
                tb._toolbox_state.selected_element_path = ep_live
                tb._restore_selected_element_path()

        asyncio.create_task(more_snappy())


def _element_from_js_event(event):
    return get_deepest_element(event.clientX, event.clientY)


def _pretty(node: js.HTMLElement):
    if hasattr(node, 'tagName'):
        identifier = node.dataset.name if node.hasAttribute('data-name') else node.id
        return f'{node.tagName.lower()}#{identifier}.{node.className}[{node.innerHTML.strip()[:20]}…]'
    return str(node)


_style = """
/* Global body styles for transitions */
    body {
    transition: padding 0.3s ease;
}

/* Disable transitions during resize for better performance */
    body.sidebar-resizing {
    transition: none !important;
}

body.sidebar-resizing * {
    transition: none !important;
}

/* Sidebar content styles */
.sidebar-content {
    padding: 15px;
}

.sidebar-menu {
    list-style: none;
padding: 0;
margin: 0;
}

.sidebar-menu li {
    padding: 10px 15px;
border-bottom: 1px solid rgba(255,255,255,0.1);
cursor: pointer;
}

.sidebar-menu li:hover {
    background-color: rgba(255,255,255,0.05);
}
"""

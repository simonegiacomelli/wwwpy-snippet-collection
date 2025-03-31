from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging
import datetime

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

    def init_component(self):
        """Initialize the sidebar demo component with shadow DOM"""
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
                color: #333;
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
        
        <!-- The pushable-sidebar component -->
        <pushable-sidebar data-name="sidebar" position="left" width="300px">
            <div class="sidebar-content">
                <h3>Pushable Sidebar</h3>
                <p>This is a sidebar that doesn't overlap content.</p>
                <ul class="sidebar-menu">
                    <li>Dashboard</li>
                    <li>Profile</li>
                    <li>Settings</li>
                    <li>Notifications</li>
                    <li>Help</li>
                </ul>
            </div>
        </pushable-sidebar>
        
        <!-- Main content -->
        <div class="content">
            <h1>Pushable Sidebar Demo</h1>
            
            <p>This demo shows how to use the PushableSidebar library to create sidebars that push content away instead of overlapping it.</p>
            
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
        </div>
        """

        # Add global styles to the document for body transitions
        self._add_global_styles()

    def _add_global_styles(self):
        """Add global styles to document head for body transitions"""
        style = js.document.createElement('style')
        style.textContent = """
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
        self._style_element = style
        js.document.head.appendChild(style)

    async def after_init_component(self):
        """Set up event listeners after initialization"""
        # Set up event listener for sidebar state changes
        # This is needed for external events not handled by the auto-binding mechanism
        self.sidebar.element.addEventListener(
            'sidebar-state-change',
            create_proxy(self.handle_sidebar_state_change)
        )

    def connectedCallback(self):
        """Called when the element is added to the DOM"""
        pass  # Nothing special needed here

    def disconnectedCallback(self):
        """Called when the element is removed from the DOM"""
        # Remove the global styles when component is disconnected
        if hasattr(self, '_style_element') and js.document.head.contains(self._style_element):
            js.document.head.removeChild(self._style_element)

    # Event handlers using wwwpy's auto-binding with element__event naming pattern
    async def toggle_button__click(self, event):
        """Handle toggle button click"""
        self.sidebar.toggle()
        self._log(f"Sidebar toggled to state: {self.sidebar.get_state()}")

    async def add_content_button__click(self, event):
        """Handle add content button click"""
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
        """Handle state select change"""
        new_state = self.state_select.value
        self.sidebar.set_state(new_state)
        self._log(f"State changed to: {new_state}")

    async def position_select__change(self, event):
        """Handle position select change"""
        new_position = self.position_select.value
        self.sidebar.set_position(new_position)
        self._log(f"Position changed to: {new_position}")

    async def apply_width_button__click(self, event):
        """Handle apply width button click"""
        width = self.width_input.value
        self.sidebar.set_width(width)
        self._log(f"Width changed to: {width}")

    async def sidebar__sidebar_state_change(self, event):
        """Auto-bound event handler for sidebar state changes"""
        new_state = event.detail.newState
        self.state_select.value = new_state
        self._log(f"Sidebar state changed to: {new_state}")

    def handle_sidebar_state_change(self, event):
        """JavaScript event handler for sidebar state changes"""
        new_state = event.detail.newState
        self.state_select.value = new_state

    def _log(self, message: str):
        """Log a message to the console"""
        now = datetime.datetime.now()
        logger.info(f"{now} - {message}")
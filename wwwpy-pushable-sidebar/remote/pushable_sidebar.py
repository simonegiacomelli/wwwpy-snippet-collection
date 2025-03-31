from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging

logger = logging.getLogger(__name__)


class PushableSidebar(wpc.Component, tag_name='pushable-sidebar'):
    # Define attributes that match the original component's observedAttributes
    position: str = wpc.attribute()
    width: str = wpc.attribute()
    min_width: str = wpc.attribute()
    max_width: str = wpc.attribute()
    collapsed_width: str = wpc.attribute()
    z_index: str = wpc.attribute()
    state: str = wpc.attribute()

    # Element references with wwwpy's element() decorator
    _toggle_button: js.HTMLButtonElement = wpc.element()
    _close_button: js.HTMLButtonElement = wpc.element()
    _resize_handle: js.HTMLDivElement = wpc.element()
    _container: js.HTMLDivElement = wpc.element()

    def init_component(self):
        """Initialize the sidebar component"""
        # Default configuration
        self._config = {
            'position': 'left',
            'width': '300px',
            'minWidth': '50px',
            'maxWidth': '500px',
            'collapsedWidth': '30px',
            'zIndex': 9999
        }

        # Initial state
        self._state = 'expanded'

        # Resize state variables
        self._is_resizing = False
        self._start_width = 0
        self._start_x = 0

        # Create shadow DOM for style isolation
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # Apply attribute values if provided
        if self.position:
            self._config['position'] = self.position
        if self.width:
            self._config['width'] = self.width
        if self.min_width:
            self._config['minWidth'] = self.min_width
        if self.max_width:
            self._config['maxWidth'] = self.max_width
        if self.collapsed_width:
            self._config['collapsedWidth'] = self.collapsed_width
        if self.z_index:
            self._config['zIndex'] = self.z_index
        if self.state:
            self._state = self.state

        # Render the component
        self._render()

    def _render(self):
        """Create the HTML structure and CSS for the sidebar"""
        position = self._config['position']
        animation_speed = 300  # Fixed animation speed

        # Create style element
        style = js.document.createElement('style')
        # language=css
        style.textContent = f"""
        :host {{
            display: {'none' if self._state == 'hidden' else 'block'};
            position: fixed;
            top: 0;
            {position}: 0;
            height: 100%;
            box-sizing: border-box;
            z-index: {self._config['zIndex']};
            transition: width {animation_speed}ms ease;
            width: {self._config['collapsedWidth'] if self._state == 'collapsed' else self._config['width']};
            overflow: hidden;
        }}
        
        .sidebar-container {{
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
            background-color: #333;
            color: #fff;
            box-shadow: {('2px' if position == 'left' else '-2px')} 0 5px rgba(0, 0, 0, 0.1);
            box-sizing: border-box;
            transition: transform {animation_speed}ms ease;
        }}
        
        .sidebar-header {{
            display: flex;
            justify-content: {('flex-end' if position == 'left' else 'flex-start')};
            align-items: center;
            padding: 5px;
            border-bottom: 1px solid #444;
        }}
        
        .sidebar-header-buttons {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .toggle-button, .close-button {{
            background: none;
            border: none;
            cursor: pointer;
            color: #fff;
            font-size: 14px;
            padding: 3px;
            margin: 2px 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2px;
        }}
        
        .toggle-button:hover, .close-button:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        .close-button {{
            font-size: 16px;
        }}
        
        .sidebar-content {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }}
        
        .resize-handle {{
            position: absolute;
            top: 0;
            {('right' if position == 'left' else 'left')}: 0;
            width: 8px;
            height: 100%;
            cursor: {('e-resize' if position == 'left' else 'w-resize')};
            background-color: transparent;
            transition: background-color 0.2s;
            z-index: 2;
            touch-action: none;
        }}
        
        .resize-handle:hover,
        .resize-handle.active {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
        
        :host([state="collapsed"]) .sidebar-content,
        :host([state="collapsed"]) .resize-handle {{
            opacity: 0;
        }}
        
        :host([state="collapsed"]) .sidebar-header {{
            border-bottom: none;
        }}
        """

        # Create container div
        container = js.document.createElement('div')
        container.className = 'sidebar-container'
        container.setAttribute('data-name', '_container')

        # Create header with toggle and close buttons
        header = js.document.createElement('div')
        header.className = 'sidebar-header'

        button_container = js.document.createElement('div')
        button_container.className = 'sidebar-header-buttons'

        # Toggle button
        toggle_button = js.document.createElement('button')
        toggle_button.className = 'toggle-button'
        toggle_button.title = 'Expand sidebar' if self._state == 'collapsed' else 'Collapse sidebar'
        toggle_icon = '&#9658;' if (position == 'left' and self._state == 'collapsed') or \
                                   (position == 'right' and self._state != 'collapsed') else '&#9668;'
        toggle_button.innerHTML = toggle_icon
        toggle_button.setAttribute('data-name', '_toggle_button')

        # Close button
        close_button = js.document.createElement('button')
        close_button.className = 'close-button'
        close_button.title = 'Hide sidebar'
        close_button.innerHTML = '&times;'
        close_button.setAttribute('data-name', '_close_button')

        button_container.appendChild(toggle_button)
        button_container.appendChild(close_button)
        header.appendChild(button_container)

        # Create content area for slotted content
        content = js.document.createElement('div')
        content.className = 'sidebar-content'
        slot = js.document.createElement('slot')
        content.appendChild(slot)

        # Create resize handle
        resize_handle = js.document.createElement('div')
        resize_handle.className = 'resize-handle'
        resize_handle.setAttribute('data-name', '_resize_handle')

        # Assemble the sidebar
        container.appendChild(header)
        container.appendChild(content)
        container.appendChild(resize_handle)

        # Add elements to shadow DOM
        self.element.shadowRoot.appendChild(style)
        self.element.shadowRoot.appendChild(container)

    def _update_sidebar(self):
        """Update sidebar appearance and behavior based on configuration"""
        # Set attribute to match internal state
        self.element.setAttribute('state', self._state)

        # Handle display based on state
        if self._state == 'hidden':
            self.element.style.display = 'none'
            self._remove_padding()
            return
        else:
            self.element.style.display = 'block'

        # Update the width based on state
        self.element.style.width = self._config['collapsedWidth'] if self._state == 'collapsed' else self._config['width']

        # Update toggle button icon and title
        if hasattr(self, '_toggle_button') and self._toggle_button:
            position = self._config['position']
            toggle_icon = '&#9658;' if (position == 'left' and self._state == 'collapsed') or \
                                       (position == 'right' and self._state != 'collapsed') else '&#9668;'
            self._toggle_button.innerHTML = toggle_icon
            self._toggle_button.title = 'Expand sidebar' if self._state == 'collapsed' else 'Collapse sidebar'

        # Update document body padding
        self._adjust_content_padding()

    def _adjust_content_padding(self):
        """Adjust body padding to accommodate the sidebar"""
        # Remove existing padding first
        self._remove_padding()

        # Skip adding padding if sidebar is hidden
        if self._state == 'hidden':
            return

        # Add padding based on current sidebar state
        current_width = self._config['collapsedWidth'] if self._state == 'collapsed' else \
            self.element.style.width or self._config['width']

        # Calculate padding with the px suffix if needed
        padding_value = current_width if current_width.endswith('px') else f"{current_width}px"

        # Apply padding to body to push content
        if self._config['position'] == 'left':
            js.document.body.style.paddingLeft = padding_value
        else:
            js.document.body.style.paddingRight = padding_value

        # Dispatch event for external components to react
        self.element.dispatchEvent(
            js.CustomEvent.new('sidebar-resize', dict_to_js({
                'detail': {'width': current_width}
            }))
        )

    def _remove_padding(self):
        """Remove body padding"""
        if self._config['position'] == 'left':
            js.document.body.style.paddingLeft = ''
        else:
            js.document.body.style.paddingRight = ''

    async def _resize_handle__mousedown(self, event):
        """Start resize operation (using wwwpy's naming convention for event handlers)"""
        # If sidebar is in collapsed state, expand it first but keep the current width
        if self._state == 'collapsed':
            current_width = self.element.style.width
            self.set_state('expanded')
            self.element.style.width = current_width  # Prevent jumping to stored width

        self._is_resizing = True
        self._start_width = int(js.getComputedStyle(self.element).width.replace('px', ''))
        self._start_x = event.clientX

        # Add active class to handle
        self._resize_handle.classList.add('active')

        # Set up mousemove and mouseup handlers directly on document
        self._mousemove_handler = create_proxy(self._handle_resize)
        self._mouseup_handler = create_proxy(self._stop_resize)

        js.document.addEventListener('mousemove', self._mousemove_handler)
        js.document.addEventListener('mouseup', self._mouseup_handler)
        js.document.addEventListener('mouseleave', self._mouseup_handler)

        # Prevent text selection during resize
        js.document.body.style.userSelect = 'none'

        # Add a resize class to the body to optimize rendering
        js.document.body.classList.add('sidebar-resizing')

        event.preventDefault()

    def _handle_resize(self, event):
        """Handle resize during mouse move"""
        if not self._is_resizing:
            return

        # Calculate new width
        if self._config['position'] == 'left':
            new_width = self._start_width + (event.clientX - self._start_x)
        else:
            new_width = self._start_width - (event.clientX - self._start_x)

        # Apply min/max constraints
        min_width = int(self._config['minWidth'].replace('px', ''))
        max_width = int(self._config['maxWidth'].replace('px', ''))

        if new_width < min_width:
            new_width = min_width
        if new_width > max_width:
            new_width = max_width

        # Update the sidebar width
        self.element.style.width = f"{new_width}px"

        # Update body padding
        if self._config['position'] == 'left':
            js.document.body.style.paddingLeft = f"{new_width}px"
        else:
            js.document.body.style.paddingRight = f"{new_width}px"

    def _stop_resize(self, event):
        """End resize operation"""
        if not self._is_resizing:
            return

        self._is_resizing = False
        self._resize_handle.classList.remove('active')

        # Clean up event listeners
        js.document.removeEventListener('mousemove', self._mousemove_handler)
        js.document.removeEventListener('mouseup', self._mouseup_handler)
        js.document.removeEventListener('mouseleave', self._mouseup_handler)

        # Restore text selection
        js.document.body.style.userSelect = ''

        # Remove resize class
        js.document.body.classList.remove('sidebar-resizing')

        # Store the final width in the config
        width_val = self.element.style.width
        if width_val.endswith('px'):
            width_px = int(width_val.replace('px', ''))
            self._config['width'] = f"{width_px}px"
        else:
            self._config['width'] = width_val

        # Save the current width to localStorage if desired
        try:
            js.localStorage.setItem('pushable-sidebar-width', self._config['width'])
        except:
            pass

        # Fire an event for the resize completion
        self.element.dispatchEvent(
            js.CustomEvent.new('sidebar-resize-end', dict_to_js({
                'detail': {'width': self._config['width']}
            }))
        )

    async def _toggle_button__click(self, event):
        """Handle toggle button click - uses wwwpy's automatic event binding"""
        self.toggle()

    async def _close_button__click(self, event):
        """Handle close button click - uses wwwpy's automatic event binding"""
        self.set_state('hidden')

    # Public API methods
    def set_state(self, state):
        """Set sidebar state ('hidden', 'collapsed', 'expanded')"""
        if state not in ['hidden', 'collapsed', 'expanded']:
            logger.warning('Invalid state. Valid states are: hidden, collapsed, expanded')
            return self

        old_state = self._state
        self._state = state
        self._update_sidebar()

        # Dispatch event
        self.element.dispatchEvent(
            js.CustomEvent.new('sidebar-state-change', dict_to_js({
                'detail': {
                    'oldState': old_state,
                    'newState': state
                }
            }))
        )

        return self

    def get_state(self):
        """Get current state"""
        return self._state

    def toggle(self):
        """Toggle sidebar state: expanded <-> collapsed, or hidden -> expanded"""
        if self._state == 'hidden':
            self.set_state('expanded')
        elif self._state == 'expanded':
            self.set_state('collapsed')
        else:  # collapsed
            self.set_state('expanded')
        return self

    def set_width(self, width):
        """Set sidebar width programmatically"""
        self._config['width'] = width
        if self._state == 'expanded':
            self.element.style.width = width
            self._adjust_content_padding()
        return self

    def set_position(self, position):
        """Set sidebar position"""
        if position not in ['left', 'right']:
            logger.warning('Sidebar position must be "left" or "right"')
            return self

        # Remove current positioning
        self._remove_padding()

        # Update position
        self._config['position'] = position
        self.element.setAttribute('position', position)

        # Re-render the sidebar
        while self.element.shadowRoot.firstChild:
            self.element.shadowRoot.removeChild(self.element.shadowRoot.firstChild)

        self._render()
        self._update_sidebar()

        return self

    # Lifecycle callbacks from the web components spec
    def connectedCallback(self):
        """Called when the element is added to the DOM"""
        # Update the sidebar when connected
        self._update_sidebar()

        # Add resize event listener for responsive behavior
        self._window_resize_handler = create_proxy(lambda event: self._adjust_content_padding())
        js.window.addEventListener('resize', self._window_resize_handler)

    def disconnectedCallback(self):
        """Called when the element is removed from the DOM"""
        # Remove the padding from body when sidebar is removed
        self._remove_padding()

        # Clean up event listeners
        if hasattr(self, '_window_resize_handler'):
            js.window.removeEventListener('resize', self._window_resize_handler)

    def attributeChangedCallback(self, name, old_value, new_value):
        """Called when an observed attribute changes"""
        if old_value == new_value:
            return

        # Convert kebab-case to camelCase for some attribute names
        if name == 'position':
            self._config['position'] = new_value
        elif name == 'width':
            self._config['width'] = new_value
        elif name == 'min-width':
            self._config['minWidth'] = new_value
        elif name == 'max-width':
            self._config['maxWidth'] = new_value
        elif name == 'collapsed-width':
            self._config['collapsedWidth'] = new_value
        elif name == 'z-index':
            self._config['zIndex'] = new_value
        elif name == 'state':
            if new_value in ['hidden', 'collapsed', 'expanded']:
                self._state = new_value
            else:
                logger.warning('Invalid state. Valid values are: hidden, collapsed, expanded')

        # Update the sidebar if it's already connected
        if self.element.isConnected:
            self._update_sidebar()
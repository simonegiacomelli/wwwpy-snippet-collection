from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging

logger = logging.getLogger(__name__)


class PopupNotificationElement(wpc.Component, tag_name='popup-notification'):
    """A popup notification component that can display different types of notifications."""

    # Attributes
    position: str = wpc.attribute()
    """Position of the notifications: right-bottom (default), left-bottom, right-top, or left-top"""

    # Container for popups
    container: js.HTMLDivElement = wpc.element()
    """The container element for popups"""

    def init_component(self):
        """Initialize the component."""
        # Initialize properties
        self.MAX_VISIBLE = 5
        self.DEFAULT_TIMEOUT = 5000
        self.activePopups = []
        self.popupQueue = []

        # Create shadow DOM
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # Render shadow DOM content
        self._render()

        # Cache container reference
        self.container = self.element.shadowRoot.querySelector('.popup-container')

    def connectedCallback(self):
        """Called when the element is added to the DOM."""
        # Set the position from attribute
        self.position = self.element.getAttribute('position') or 'right-bottom'
        self.container.className = f"popup-container {self.position}"

    def attributeChangedCallback(self, name, oldValue, newValue):
        """Called when an observed attribute changes."""
        if name == 'position' and oldValue != newValue:
            self.container.className = f"popup-container {newValue}"

    def getIconSvg(self, notification_type):
        """Get the SVG icon for a notification type."""
        if notification_type == 'info':
            return '<svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'
        elif notification_type == 'warning':
            return '<svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>'
        elif notification_type == 'error':
            return '<svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>'
        elif notification_type == 'success':
            return '<svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'
        else:
            return '<svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'

    def getTypeTitle(self, notification_type):
        """Get the title for a notification type."""
        return notification_type.capitalize()

    def createPopupElement(self, options):
        """Create a popup notification element based on options."""
        # Create popup element
        popup = js.document.createElement('div')
        popup.className = f"popup-notification {options['type']}"
        popup.setAttribute('role', 'alert')
        popup.setAttribute('aria-live', 'polite')

        # Create header
        header = js.document.createElement('div')
        header.className = 'popup-header'

        icon = js.document.createElement('div')
        icon.className = 'popup-icon'
        icon.innerHTML = self.getIconSvg(options['type'])

        title = js.document.createElement('h3')
        title.className = 'popup-title'
        title.textContent = self.getTypeTitle(options['type'])

        closeBtn = js.document.createElement('button')
        closeBtn.className = 'popup-close'
        closeBtn.setAttribute('aria-label', 'Close')
        closeBtn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>'

        # Add close event listener
        closeBtn.addEventListener('click', create_proxy(lambda event: self.close(popup)))

        header.appendChild(icon)
        header.appendChild(title)
        header.appendChild(closeBtn)

        # Create content
        content = js.document.createElement('div')
        content.className = 'popup-content'

        if isinstance(options['message'], str):
            content.innerHTML = options['message']
        elif hasattr(options['message'], 'nodeType'):
            content.appendChild(options['message'].cloneNode(True))

        # Create actions if provided
        actions = None
        if options.get('actions') and len(options['actions']) > 0:
            actions = js.document.createElement('div')
            actions.className = 'popup-actions'

            for action in options['actions']:
                button = js.document.createElement('button')
                button.className = f"popup-action {'primary' if action.get('primary') else ''}"
                button.textContent = action['label']

                # Use create_proxy to properly handle JavaScript callbacks
                button.addEventListener('click', create_proxy(lambda event, a=action: self._handle_action_click(event, a, popup)))

                actions.appendChild(button)

        # Create progress bar for auto-close
        progress = js.document.createElement('div')
        progress.className = 'popup-progress'

        progressFill = js.document.createElement('div')
        progressFill.className = 'popup-progress-fill'
        progress.appendChild(progressFill)

        # Build the popup
        popup.appendChild(header)
        popup.appendChild(content)
        if actions:
            popup.appendChild(actions)
        popup.appendChild(progress)

        # Setup auto-close
        popup.timeoutId = None
        popup.pausedAt = None

        if options.get('autoClose', True) and options.get('timeout', 0) > 0:
            progressFill.style.backgroundColor = 'currentColor'
            progressFill.style.transition = f"transform {options['timeout'] / 1000}s linear"

            # Start the animation after a small delay
            js.setTimeout(lambda: setattr(progressFill.style, 'transform', 'scaleX(0)'), 10)

            # Set timeout to close the popup
            popup.timeoutId = js.setTimeout(create_proxy(lambda: self.close(popup)), options['timeout'])

            # Pause on hover/focus for accessibility
            popup.addEventListener('mouseenter', create_proxy(lambda e: self._pause_auto_close(popup, progressFill, progress)))
            popup.addEventListener('mouseleave', create_proxy(lambda e: self._resume_auto_close(popup, progressFill, options['timeout'])))
            popup.addEventListener('focus', create_proxy(lambda e: self._pause_auto_close(popup, progressFill, progress)), True)
            popup.addEventListener('blur', create_proxy(lambda e: self._resume_auto_close(popup, progressFill, options['timeout'])), True)
        else:
            progress.style.display = 'none'

        # Add keyboard accessibility
        popup.tabIndex = 0
        popup.addEventListener('keydown', create_proxy(lambda e: self.close(popup) if e.key == 'Escape' else None))

        # Store callbacks
        popup.callbacks = {
            'onBeforeShow': options.get('onBeforeShow'),
            'onAfterShow': options.get('onAfterShow'),
            'onBeforeHide': options.get('onBeforeHide'),
            'onAfterHide': options.get('onAfterHide')
        }

        return popup

    def _handle_action_click(self, event, action, popup):
        """Handle action button clicks."""
        if action.get('callback') and callable(action['callback']):
            action['callback'](event)

        if action.get('closeOnClick', True):
            self.close(popup)

    def _pause_auto_close(self, popup, progressFill, progress):
        """Pause the auto-close timer when hovering or focusing."""
        if popup.timeoutId:
            js.clearTimeout(popup.timeoutId)
            progressFill.style.transitionProperty = 'none'
            popup.pausedAt = progressFill.getBoundingClientRect().width / progress.getBoundingClientRect().width
            progressFill.style.transform = f"scaleX({popup.pausedAt})"

    def _resume_auto_close(self, popup, progressFill, timeout):
        """Resume the auto-close timer after pausing."""
        if popup.pausedAt is None:
            return

        remainingTime = timeout * popup.pausedAt
        progressFill.style.transition = f"transform {remainingTime / 1000}s linear"
        progressFill.style.transform = 'scaleX(0)'

        popup.timeoutId = js.setTimeout(create_proxy(lambda: self.close(popup)), remainingTime)

    def processQueue(self):
        """Process the queue of popups waiting to be shown."""
        if len(self.popupQueue) > 0 and len(self.activePopups) < self.MAX_VISIBLE:
            options = self.popupQueue.pop(0)
            self.show(options)

    def show(self, options):
        """Show a popup notification with the given options."""
        # Handle simple string case
        if isinstance(options, str):
            options = {'message': options}

        # Set default options
        config = {
            'message': '',
            'type': 'info',
            'timeout': self.DEFAULT_TIMEOUT,
            'autoClose': True,
            'actions': []
        }
        config.update(options)

        # Check if we've hit the maximum number of visible popups
        if len(self.activePopups) >= self.MAX_VISIBLE:
            self.popupQueue.append(config)
            return None

        # Call before show callback
        if config.get('onBeforeShow') and callable(config['onBeforeShow']):
            config['onBeforeShow']()

        # Create and add the popup element
        popup = self.createPopupElement(config)
        self.container.appendChild(popup)
        self.activePopups.append(popup)

        # Call after show callback
        if popup.callbacks.get('onAfterShow') and callable(popup.callbacks['onAfterShow']):
            js.setTimeout(create_proxy(lambda: popup.callbacks['onAfterShow']()), 300)

        return popup

    def close(self, popup):
        """Close a specific popup notification."""
        # Check if popup exists in active popups
        try:
            index = self.activePopups.index(popup)
        except ValueError:
            return False

        # Clear any existing timeout
        if popup.timeoutId:
            js.clearTimeout(popup.timeoutId)

        # Call before hide callback
        if popup.callbacks.get('onBeforeHide') and callable(popup.callbacks['onBeforeHide']):
            popup.callbacks['onBeforeHide']()

        # Add closing animation
        popup.classList.add('closing')

        # Define the animationend handler
        def on_animation_end(event):
            # Remove from activePopups
            try:
                index = self.activePopups.index(popup)
                self.activePopups.pop(index)
            except ValueError:
                pass

            # Remove from DOM
            if popup.parentNode:
                popup.parentNode.removeChild(popup)

            # Call after hide callback
            if popup.callbacks.get('onAfterHide') and callable(popup.callbacks['onAfterHide']):
                popup.callbacks['onAfterHide']()

            # Process queue
            self.processQueue()

        # Wait for animation to complete, then remove
        popup.addEventListener('animationend', create_proxy(on_animation_end), {'once': True})

        return True

    def closeAll(self):
        """Close all active popups."""
        # Make a copy of the list since we'll be modifying it
        popups_to_close = self.activePopups.copy()

        # Close all active popups
        for popup in popups_to_close:
            self.close(popup)

        # Clear queue
        self.popupQueue = []

    def info(self, options):
        """Show an info notification."""
        if isinstance(options, str):
            options = {'message': options}

        options['type'] = 'info'
        return self.show(options)

    def warning(self, options):
        """Show a warning notification."""
        if isinstance(options, str):
            options = {'message': options}

        options['type'] = 'warning'
        return self.show(options)

    def error(self, options):
        """Show an error notification."""
        if isinstance(options, str):
            options = {'message': options}

        options['type'] = 'error'
        return self.show(options)

    def success(self, options):
        """Show a success notification."""
        if isinstance(options, str):
            options = {'message': options}

        options['type'] = 'success'
        return self.show(options)

    def _render(self):
        """Add styles and container to shadow DOM."""
        # language=html
        self.element.shadowRoot.innerHTML = """
            <style>
                /* Host styles and CSS Custom Properties */
                :host {
                    --popup-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    --popup-font-size: 14px;
                    --popup-line-height: 1.6;
                }

                /* Popup notification styles */
                .popup-container {
                    position: fixed;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    pointer-events: none;
                    font-family: var(--popup-font-family);
                    font-size: var(--popup-font-size);
                    line-height: var(--popup-line-height);
                }

                .popup-container.right-bottom {
                    bottom: 20px;
                    right: 20px;
                    align-items: flex-end;
                }

                .popup-container.left-bottom {
                    bottom: 20px;
                    left: 20px;
                    align-items: flex-start;
                }

                .popup-container.right-top {
                    top: 20px;
                    right: 20px;
                    align-items: flex-end;
                }

                .popup-container.left-top {
                    top: 20px;
                    left: 20px;
                    align-items: flex-start;
                }

                .popup-notification {
                    margin-top: 10px;
                    background-color: white;
                    border-radius: 4px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    min-width: 280px;
                    max-width: 320px;
                    overflow: hidden;
                    pointer-events: auto;
                    animation: slideIn 0.3s ease-out forwards;
                    font-family: var(--popup-font-family);
                }

                .popup-notification.closing {
                    animation: slideOut 0.3s ease-in forwards;
                }

                .popup-header {
                    display: flex;
                    align-items: center;
                    padding: 12px 12px 0 12px;
                }

                .popup-icon {
                    margin-right: 8px;
                    display: flex;
                    align-items: center;
                }

                .popup-title {
                    flex-grow: 1;
                    font-weight: bold;
                    margin: 0;
                    font-size: 16px;
                    font-family: var(--popup-font-family);
                }

                .popup-close {
                    background: none;
                    border: none;
                    cursor: pointer;
                    color: #888;
                    padding: 4px;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: var(--popup-font-family);
                }

                .popup-close:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }

                .popup-content {
                    padding: 8px 12px;
                    word-break: break-word;
                    font-family: var(--popup-font-family);
                }

                .popup-actions {
                    display: flex;
                    padding: 8px 12px 12px;
                    justify-content: flex-end;
                    gap: 8px;
                }

                .popup-action {
                    padding: 6px 12px;
                    border: none;
                    background-color: #f0f0f0;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-family: var(--popup-font-family);
                }

                .popup-action:hover {
                    background-color: #e0e0e0;
                }

                .popup-action.primary {
                    background-color: #2196F3;
                    color: white;
                }

                .popup-action.primary:hover {
                    background-color: #1976D2;
                }

                .popup-progress {
                    height: 4px;
                    width: 100%;
                    background-color: rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }

                .popup-progress-fill {
                    height: 100%;
                    width: 100%;
                    transform-origin: left;
                    transform: scaleX(1);
                    transition: transform linear;
                }

                /* Type-specific styles */
                .popup-notification.info {
                    border-top: 3px solid #2196F3;
                }

                .popup-notification.info .popup-icon,
                .popup-notification.info .popup-title,
                .popup-notification.info .popup-progress-fill {
                    color: #2196F3;
                }

                .popup-notification.warning {
                    border-top: 3px solid #FF9800;
                }

                .popup-notification.warning .popup-icon,
                .popup-notification.warning .popup-title,
                .popup-notification.warning .popup-progress-fill {
                    color: #FF9800;
                }

                .popup-notification.error {
                    border-top: 3px solid #F44336;
                }

                .popup-notification.error .popup-icon,
                .popup-notification.error .popup-title,
                .popup-notification.error .popup-progress-fill {
                    color: #F44336;
                }

                .popup-notification.success {
                    border-top: 3px solid #4CAF50;
                }

                .popup-notification.success .popup-icon,
                .popup-notification.success .popup-title,
                .popup-notification.success .popup-progress-fill {
                    color: #4CAF50;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(120%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @keyframes slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(120%);
                        opacity: 0;
                    }
                }

                /* Reduced motion */
                @media (prefers-reduced-motion: reduce) {
                    .popup-notification, .popup-notification.closing {
                        animation: none;
                    }
                }
            </style>

            <div class="popup-container right-bottom"></div>
        """



from __future__ import annotations

import asyncio

import js
from wwwpy.remote import component as wpc, dict_to_js

from remote.popup_notification import PopupNotificationElement, logger


class PopupDemoElement(wpc.Component, tag_name='popup-demo'):
    """A demo component for the popup notification system."""

    # Button elements
    basic_popup: js.HTMLButtonElement = wpc.element()
    info_popup: js.HTMLButtonElement = wpc.element()
    warning_popup: js.HTMLButtonElement = wpc.element()
    error_popup: js.HTMLButtonElement = wpc.element()
    success_popup: js.HTMLButtonElement = wpc.element()
    custom_popup: js.HTMLButtonElement = wpc.element()
    multiple_popups: js.HTMLButtonElement = wpc.element()
    close_all_popups: js.HTMLButtonElement = wpc.element()

    # Popup notification element
    popup_notification: PopupNotificationElement = wpc.element()

    def init_component(self):
        """Initialize the component."""
        # Create shadow DOM
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # Render shadow DOM content
        self._render()


    def _render(self):
        """Add styles and structure to shadow DOM."""
        # language=html
        self.element.shadowRoot.innerHTML = """
            <style>
                /* Demo section styles */
                .demo-section {
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }

                button {
                    padding: 8px 16px;
                    margin: 5px;
                    border: none;
                    border-radius: 4px;
                    background-color: #4CAF50;
                    color: white;
                    cursor: pointer;
                    font-weight: bold;
                }

                button:hover {
                    background-color: #45a049;
                }

                button.error {
                    background-color: #f44336;
                }

                button.error:hover {
                    background-color: #d32f2f;
                }

                button.warning {
                    background-color: #ff9800;
                }

                button.warning:hover {
                    background-color: #f57c00;
                }

                button.info {
                    background-color: #2196f3;
                }

                button.info:hover {
                    background-color: #1976d2;
                }
            </style>

            <!-- Local popup-notification element inside the demo -->
            <popup-notification position="right-bottom" data-name="popup_notification"></popup-notification>

            <div class="demo-section">
                <button data-name="basic_popup">Basic Popup</button>
                <button data-name="info_popup" class="info">Info</button>
                <button data-name="warning_popup" class="warning">Warning</button>
                <button data-name="error_popup" class="error">Error</button>
                <button data-name="success_popup">Success</button>
                <button data-name="custom_popup">Custom Popup</button>
                <button data-name="multiple_popups">Show Multiple</button>
                <button data-name="close_all_popups">Close All</button>
            </div>
        """

    async def basic_popup__click(self, event):
        """Show a basic popup notification."""
        logger.debug('Showing basic popup')
        self.popup_notification.show('This is a basic notification')

    async def info_popup__click(self, event):
        """Show an info popup notification."""
        logger.debug('Showing info popup')
        self.popup_notification.info('This is an info notification with some details')

    async def warning_popup__click(self, event):
        """Show a warning popup notification."""
        logger.debug('Showing warning popup')
        self.popup_notification.warning({
            'message': 'Warning! Something needs your attention',
            'timeout': 7000
        })

    async def error_popup__click(self, event):
        """Show an error popup notification."""
        logger.debug('Showing error popup')
        self.popup_notification.error({
            'message': 'Error: Something went wrong!',
            'timeout': 8000
        })

    async def success_popup__click(self, event):
        """Show a success popup notification."""
        logger.debug('Showing success popup')
        self.popup_notification.success('Success! Operation completed')

    async def custom_popup__click(self, event):
        """Show a custom popup notification with actions."""
        logger.debug('Showing custom popup')

        def confirm_callback(e):
            logger.debug('Confirmed!')

        def cancel_callback(e):
            logger.debug('Cancelled!')

        def after_hide_callback():
            logger.debug('Notification closed')

        self.popup_notification.show({
            'message': 'Custom notification with actions',
            'type': 'warning',
            'timeout': 0,  # Disable auto-close
            'actions': [
                {
                    'label': 'Confirm',
                    'callback': confirm_callback,
                    'closeOnClick': True,
                    'primary': True
                },
                {
                    'label': 'Cancel',
                    'callback': cancel_callback
                }
            ],
            'onAfterHide': after_hide_callback
        })

    async def multiple_popups__click(self, event):
        """Show multiple popup notifications in succession."""
        logger.debug('Showing multiple popups')

        # We'll use a helper function to show popups with delay
        async def show_popup_with_delay(index):
            types = ['info', 'warning', 'error', 'success']
            notification_type = types[index % len(types)]

            method = getattr(self.popup_notification, notification_type)
            method({
                'message': f'Notification #{index + 1} ({notification_type})',
                'timeout': 8000 + (index * 500)
            })

        # Show 5 notifications in quick succession
        for i in range(5):
            # Use asyncio.sleep for delay
            asyncio.create_task(
                self._show_delayed_popup(i)
            )

    async def _show_delayed_popup(self, index):
        """Helper method to show a popup after a delay."""
        await asyncio.sleep(index * 0.3)  # 300ms between each popup

        types = ['info', 'warning', 'error', 'success']
        notification_type = types[index % len(types)]

        method = getattr(self.popup_notification, notification_type)
        method({
            'message': f'Notification #{index + 1} ({notification_type})',
            'timeout': 8000 + (index * 500)
        })

    async def close_all_popups__click(self, event):
        """Close all popup notifications."""
        logger.debug('Closing all popups')
        self.popup_notification.closeAll()

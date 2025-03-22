import asyncio
import inspect
import wwwpy.remote.component as wpc
import js

import logging

from remote.spinner_overlay_component import spinner

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _overlay: js.HTMLButtonElement = wpc.element()
    _small: js.HTMLButtonElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """

<button data-name="_overlay">Overlay spinner for 3 seconds</button>
<button data-name="_small">Small spinner for 3 seconds</button>

"""

    async def _overlay__click(self, event):
        async with spinner():
            await asyncio.sleep(3)
    
    async def _small__click(self, event):
        async with spinner(small=True):
            await asyncio.sleep(3)

    
    
import logging

import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class _BaseSpinnerComponent(wpc.Component):
    _counter: int

    def init_component(self):
        self._counter = 0

    async def show(self):
        self._counter += 1
        self.element.style.display = 'block'

    async def hide(self):
        self._counter -= 1
        if self._counter <= 0:
            self._counter = 0
            self.element.style.display = 'none'


class SpinnerOverlayComponent(_BaseSpinnerComponent, tag_name='spinner-overlay'):
    _overlay: js.HTMLDivElement = wpc.element()

    def init_component(self):
        super().init_component()
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
    <style>    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    
    <div data-name="_overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000;">
        <div style="background-color: #222; padding: 30px; border-radius: 8px; text-align: center; box-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);">
            <div style="width: 50px; height: 50px; border: 5px solid rgba(255, 255, 255, 0.1); border-top: 5px solid #3498db; border-radius: 50%; margin: 0 auto 20px; animation: spin 1s linear infinite;"></div>
            <p style="color: #e0e0e0; font-size: 16px; margin: 0;">Loading...</p>
        </div>
    </div>
"""


class SpinnerSmallComponent(_BaseSpinnerComponent, tag_name='spinner-small'):
    _spinner: js.HTMLDivElement = wpc.element()

    def init_component(self):
        super().init_component()
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
    <style>    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }    
    </style>
    
    <div data-name="_spinner" style="position: fixed; top: 20px; left: 20px; z-index: 1000;">
        <div style="width: 30px; height: 30px; border: 3px solid rgba(52, 152, 219, 0.2); border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
    </div>
"""


def _global_instance(cls: type[_BaseSpinnerComponent], id_name: str | None = None) -> _BaseSpinnerComponent:
    if id_name is None:
        id_name = 'id_' + cls.component_metadata.tag_name
    tag_name = cls.component_metadata.tag_name
    instance = _single_tag_instance(tag_name, id_name)
    comp = wpc.get_component(instance)
    assert isinstance(comp, cls), f'Expected {cls}, tag_name={tag_name}, got {comp}, from element {instance}'
    return comp


def _single_tag_instance(tag_name, global_id):
    ele = js.document.getElementById(global_id)
    if ele is None:
        ele = js.document.createElement(tag_name)
        ele.id = global_id
        js.document.body.appendChild(ele)
    return ele


from contextlib import asynccontextmanager


@asynccontextmanager
async def spinner(small: bool = False):
    """
    Async context manager for the spinner overlay.
    Shows the spinner when entering the context and hides it when exiting.

    Usage:
        async with spinner_context():
            # Your async code here
    """
    s = _global_instance(SpinnerSmallComponent if small else SpinnerOverlayComponent)
    try:
        await s.show()
        yield
    finally:
        await s.hide()

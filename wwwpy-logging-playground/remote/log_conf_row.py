import inspect
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class LogConfRow(wpc.Component, tag_name='log-conf-row'):
    _level_select: js.HTMLSelectElement = wpc.element()
    _logger_name: js.HTMLSpanElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """       
<div>         
    <select data-name="_level_select"></select>
    <span data-name="_logger_name">_logger_name</span>
</div>
"""

        self._level_select.innerHTML = ''
        items = list(logging.getLevelNamesMapping().items())
        items.sort(key=lambda x: x[1])
        for name, level in items:
            option = js.document.createElement('option')
            option.value = name
            if level != logging.NOTSET:
                option.innerText = name
            self._level_select.appendChild(option)

    @property
    def level_select(self) -> str:
        return self._level_select.value

    @level_select.setter
    def level_select(self, level_name: str):
        self._level_select.value = level_name

    @property
    def logger_name(self) -> str:
        return self._logger_name.innerText

    @logger_name.setter
    def logger_name(self, name: str):
        self._logger_name.innerText = name

    async def _level_select__input(self, event):
        js.document.dispatchEvent(
            js.CustomEvent.new('input-row', dict_to_js(
                {
                    'detail': self
                }))
        )

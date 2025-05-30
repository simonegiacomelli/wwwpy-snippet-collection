import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)


class LogConfRow(wpc.Component, tag_name='log-conf-row'):
    level_select: js.HTMLSelectElement = wpc.element()
    logger_name: js.HTMLSpanElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """       
<div>         
    <select data-name="level_select"></select>
    <span data-name="logger_name">logger_name</span>
</div>
"""

        self.level_select.innerHTML = ''
        items = list(logging.getLevelNamesMapping().items())
        items.sort(key=lambda x:  x[1])
        for name, level in items:
            option = js.document.createElement('option')
            option.value = name
            if level != logging.NOTSET:
                option.innerText = name
            self.level_select.appendChild(option)
    

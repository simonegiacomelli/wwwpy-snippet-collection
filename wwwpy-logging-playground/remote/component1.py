from remote.log_conf_row import LogConfRow
import inspect
import js
import logging

import wwwpy.remote.component as wpc

logger = logging.getLogger(__name__)
from . import log_conf_row  # noqa


class Component1(wpc.Component, tag_name='component-1'):
    _rescan: js.HTMLButtonElement = wpc.element()
    _ta_log: js.HTMLTextAreaElement = wpc.element()
    _title: js.HTMLDivElement = wpc.element()
    _row_container: js.HTMLDivElement = wpc.element()
    _search: js.HTMLInputElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>hello
<button data-name="_rescan">_rescan</button></div>

<div data-name="_title">_title</div><textarea data-name="_ta_log" placeholder="textarea1" rows="8" wrap="off" style="width: 100%"></textarea>




<input data-name="_search" placeholder="Filter by logger name">
<div data-name="_row_container"><br></div> 
"""
        self._list_all_logger()

    def _list_all_logger(self):
        import logging

        items = [(n, l) for n, l in logging.root.manager.loggerDict.items() if isinstance(l, logging.Logger)]
        # items.sort(key=lambda x: (x[1].level, x[0]), reverse=True)  # sort by logger name
        items.sort(key=lambda t: - t[1].level)
        items.sort(key=lambda t: t[0].lower())
        self._title.innerText = f'Found {len(items)} loggers'
        self._row_container.innerHTML = ''  # clear previous rows
        for name, logger in items:
            search_value = self._search.value.lower()
            if search_value and search_value not in name.lower():
                continue
            level_name = '' if logger.level == logging.NOTSET else logging.getLevelName(logger.level)
            line = f"{level_name:<10} {name}"
            self._log(line)
            row = log_conf_row.LogConfRow()
            row.logger_name = name
            row.level_select = level_name
            self._row_container.appendChild(row.element)
        # scroll to the top of the log area
        self._ta_log.scrollTop = 0

    def _log(self, message):
        if not isinstance(message, str):
            message = str(message)
        self._ta_log.value += f"{message}\n"
        self._ta_log.scrollTop = self._ta_log.scrollHeight

    async def _rescan__click(self, event):
        self._list_all_logger()

    async def _row_container__input_row(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        row: LogConfRow = event.detail
        logger.debug(f'LogConfRow: _row_container__input_row: {row.logger_name} level={row.level_select}')
        logging.getLogger(row.logger_name).setLevel(row.level_select)
        
    
    async def _search__input(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        self._list_all_logger()
    
    


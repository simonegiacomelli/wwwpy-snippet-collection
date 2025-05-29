import inspect
import js
import logging

import wwwpy.remote.component as wpc

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _rescan: js.HTMLButtonElement = wpc.element()
    _ta_log: js.HTMLTextAreaElement = wpc.element()
    _title: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>hello
<button data-name="_rescan">_rescan</button></div>

<div data-name="_title">_title</div><textarea data-name="_ta_log" placeholder="textarea1" rows="20" wrap="off" style="width: 100%"></textarea> 
"""
        self._list_all_logger()

    def _list_all_logger(self):
        import logging

        items = [(n, l) for n, l in logging.root.manager.loggerDict.items() if isinstance(l, logging.Logger)]
        items.sort(key=lambda x: x[1].level, reverse=True)  # sort by logger name
        self._title.innerText = f'Found {len(items)} loggers'

        for name, logger in items:
            level_name = '' if logger.level == logging.NOTSET else logging.getLevelName(logger.level)
            line = f"{level_name:<10} {name}"
            self._log(line)
        # scroll to the top of the log area
        self._ta_log.scrollTop = 0

    def _log(self, message):
        if not isinstance(message, str):
            message = str(message)
        self._ta_log.value += f"{message}\n"
        self._ta_log.scrollTop = self._ta_log.scrollHeight

    async def _rescan__click(self, event):
        self._list_all_logger()

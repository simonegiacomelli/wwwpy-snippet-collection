import inspect
import js
import logging

import wwwpy.remote.component as wpc

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    button1: js.HTMLButtonElement = wpc.element()
    _ta_log: js.HTMLTextAreaElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>hello
<button data-name="button1">button1</button></div>
<textarea data-name="_ta_log" placeholder="textarea1" rows="20" wrap="off" style="width: 100%"></textarea> 
"""
        self._list_all_logger()
    
    def _list_all_logger(self):
        import logging

        for name, logger in logging.root.manager.loggerDict.items():
            if isinstance(logger, logging.Logger):
                self._log(f"{name} level={logger.level} handlers={logger.handlers}")
    def _log(self, message):
        if not isinstance(message, str):
            message = str(message)
        self._ta_log.value += f"{message}\n"
        self._ta_log.scrollTop = self._ta_log.scrollHeight
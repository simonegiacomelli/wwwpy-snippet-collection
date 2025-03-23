import inspect
import js
import logging

import wwwpy.remote.component as wpc
from wwwpy.remote.hotkey import Hotkey

from .dialog_stack import dialog
from .upload_component import UploadComponent

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    upload1: UploadComponent = wpc.element()
    _upload: js.HTMLButtonElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<style> * { margin-bottom: 0.5em; } </style>
<div>
    
<button data-name="_upload">Upload files</button>
    
    
    <span style="display: none">
    <wwwpy-quickstart-upload data-name="upload1" style="width: 60%"></wwwpy-quickstart-upload>
    </span>
</div>               
        """
        self.upload1.multiple = True
        self.hotkey = Hotkey(js.window)
        self.hotkey.add('Escape', self._close_dialog)
        self._stored = self.upload1

    async def _upload__click(self, event):
        dialog.open(self._stored)

    def _close_dialog(self, *args):
        dialog.close(self._stored)



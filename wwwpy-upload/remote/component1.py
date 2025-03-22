import js
import logging

import wwwpy.remote.component as wpc

from .upload_component import UploadComponent

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    multiple_checkbox: js.HTMLInputElement = wpc.element()
    show_gallery: js.HTMLInputElement = wpc.element()
    icon_gallery: js.HTMLElement = wpc.element()
    upload1: UploadComponent = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<style> * { margin-bottom: 0.5em; } </style>
<div>
    <div>Component1 in component1.py</div>
    <div>The files are uploaded in the project root 'uploads' folder. To change this behaviour see file server/rpc.py</div>
    <label style="display: inline; margin-right: 2em">
        <input data-name="multiple_checkbox" type="checkbox"> Multiple files upload
    </label>
    <label style="display: inline">
        <input data-name="show_gallery" type="checkbox"> Show icon gallery
    </label>
    <hr>
    <wwwpy-icon-gallery data-name="icon_gallery" style="display: none"></wwwpy-icon-gallery>
    <p>The component below the line is defined in upload_component.py</p>
    <hr>
    <wwwpy-quickstart-upload data-name="upload1"></wwwpy-quickstart-upload>
</div>               
        """
        self.multiple_checkbox.checked = self.upload1.multiple

    async def multiple_checkbox__input(self, event):
        self.upload1.multiple = self.multiple_checkbox.checked

    async def show_gallery__input(self, event):
        self.icon_gallery.element.style.display = 'block' if self.show_gallery.checked else 'none'


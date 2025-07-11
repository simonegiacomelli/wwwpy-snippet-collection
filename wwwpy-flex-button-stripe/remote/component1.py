from __future__ import annotations

import logging
from pathlib import Path

import js
import wwwpy.remote.component as wpc
from wwwpy.common.designer.ui.icons.all_icons import AllIcons
from wwwpy.remote.designer.ui.svg_icon import SvgIcon

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _horizontal: js.HTMLDivElement = wpc.element()
    _vertical: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<hr>
<div data-name="_horizontal" style="display: inline-flex;  background-color: #2B2D30"></div>
<hr>
<div data-name="_vertical" style="display: inline-flex; flex-direction: column;  background-color: #2B2D30"></div>
<hr>
"""
        logger.debug('Adding icons')
        for svg in AllIcons.all_icons():
            logger.debug(f'Adding icon: {svg}')
            self._horizontal.appendChild(SvgIcon.from_file(svg).element)

        for svg in [AllIcons.python_stroke, AllIcons.todo_20x20_dark, AllIcons.pythonPackages_dark,
                   AllIcons.services_dark, AllIcons.console_dark]:
            self._vertical.appendChild(SvgIcon.from_file(svg).element)

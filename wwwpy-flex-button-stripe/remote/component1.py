from __future__ import annotations

import logging
from pathlib import Path

import js
import wwwpy.remote.component as wpc
import wwwpy.remote.designer.ui.new_toolbox  # noqa
from wwwpy.remote.designer.ui.new_toolbox import NewToolbox
from wwwpy.remote.designer.ui.svg_icon import SvgIcon
from .comp_tree import CompTree # noqa
logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _new_toolbox: NewToolbox = wpc.element()
    _talogs: js.HTMLTextAreaElement = wpc.element()
    div2: js.HTMLDivElement = wpc.element()
    div3: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<hr>
<wwwpy-comp-tree></wwwpy-comp-tree>
<hr>
<div data-name="div2" style="display: inline-flex;  background-color: #2B2D30"></div>
<hr>
<div data-name="div3" style="display: inline-flex; flex-direction: column;  background-color: #2B2D30"></div>
<hr>
<textarea data-name="_talogs" placeholder="textarea1" rows="6" wrap="off" style="width: 100%"></textarea>

<wwwpy-new-toolbox data-name='_new_toolbox'></wwwpy-new-toolbox>
"""
        self._new_toolbox._sidebar.element.append(js.document.createElement('hr'))
        ct = CompTree().element
        ct.style.display = 'flex'
        ct.style.height = '250px'
        ct.style.overflow = 'scroll'
        self._new_toolbox._sidebar.element.append(ct)
        self._add_svg()


    def _add_svg(self):
        folder = Path(__file__).parent
        # list all svgs
        svgs = list(folder.glob('*.svg'))
        for svg in svgs:
            # self._log(str(svg))
            self.div2.appendChild(SvgIcon.from_file(svg).element)
            self.div3.appendChild(SvgIcon.from_file(svg).element)

    def _log(self, msg):
        self._talogs.value += str(msg) + '\n'
        # scroll textarea to bottom
        self._talogs.scrollTop = self._talogs.scrollHeight

        # svg_str = add_rounded_background2(_svg1, color)



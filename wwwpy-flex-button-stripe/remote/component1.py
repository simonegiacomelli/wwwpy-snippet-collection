from __future__ import annotations
import inspect
from pathlib import Path

import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.common.designer.ui.svg import add_rounded_background2
import wwwpy.remote.designer.ui.new_toolbox  # noqa
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)

_BLUE = '#3574F0'
_GRAY = '#3C3E41'
_BGRD = '#2B2D30'


class Component1(wpc.Component, tag_name='component-1'):
    _talogs: js.HTMLTextAreaElement = wpc.element()
    div2: js.HTMLDivElement = wpc.element()
    div3: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <wwwpy-new-toolbox></wwwpy-new-toolbox>
        <div>component-1</div>
<textarea data-name="_talogs" placeholder="textarea1" rows="6" wrap="off" style="width: 100%"></textarea>
<hr>
<div data-name="div2" style="display: inline-flex;  background-color: #2B2D30"></div>
<hr>
<div data-name="div3" style="display: inline-flex; flex-direction: column;  background-color: #2B2D30"></div>

"""
        self._add_svg()

    def _add_svg(self):
        folder = Path(__file__).parent
        # list all svgs
        svgs = list(folder.glob('*.svg'))
        for svg in svgs:
            self._log(str(svg))
            self.div2.appendChild(SvgElement.from_file(svg).element)
            self.div3.appendChild(SvgElement.from_file(svg).element)

    def _log(self, msg):
        self._talogs.value += str(msg) + '\n'
        # scroll textarea to bottom
        self._talogs.scrollTop = self._talogs.scrollHeight

        # svg_str = add_rounded_background2(_svg1, color)


class SvgElement(wpc.Component, tag_name='svg-element'):
    filename: str = wpc.attribute()
    _style: js.HTMLStyleElement = wpc.element()
    _div: js.HTMLDivElement = wpc.element()
    _active: bool
    border: int = 5

    @classmethod
    def from_file(cls, file: Path) -> SvgElement:
        r = cls()
        r.load_svg_str(file.read_text())
        r.element.setAttribute('title', file.name)
        return r

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
<style data-name="_style"></style>
<div data-name="_div"></div>
        """

        self.active = False

    def load_svg_str(self, svg: str):
        self._div.innerHTML = add_rounded_background2(svg, 'var(--svg-primary-color)')

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        root, hover = (_BLUE, '') if value else (_BGRD, _GRAY)
        self._set_style(root, hover)

    def _set_style(self, color: str, hover_color: str):
        # language=html
        hover_style = ":host(:hover) { --svg-primary-color: %s; }" % (hover_color,) if hover_color else ''
        s = ('svg { display: block }\n' +
             ':host { border: %spx solid transparent }\n' % self.border +
             ':host { --svg-primary-color: %s; }\n' % color + hover_style)
        logger.debug(f'set_style: `{s}`')
        self._style.innerHTML = s

    def _div__click(self, event):
        self.active = not self.active

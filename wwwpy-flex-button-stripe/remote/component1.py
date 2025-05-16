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
    div1: js.HTMLDivElement = wpc.element()
    div2: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <wwwpy-new-toolbox></wwwpy-new-toolbox>
        <div>component-1</div>
<textarea data-name="_talogs" placeholder="textarea1" rows="6" wrap="off" style="width: 100%"></textarea>
<div data-name="div1" style="display: flex; gap: 5px;  background-color: #2B2D30"></div>
<hr>
<div data-name="div2" style="display: flex; gap: 5px;  background-color: #2B2D30"></div>

"""
        self._add_svg()

    def _add_svg(self):
        folder = Path(__file__).parent
        # list all svgs
        svgs = list(folder.glob('*.svg'))
        for svg in svgs:
            self._log(str(svg))
            svg_str = svg.read_text()
            svg_str = add_rounded_background2(svg_str, _BGRD)
            r = js.document.createRange().createContextualFragment(svg_str)
            self.div1.appendChild(r)

            svgc = SvgElement()
            svgc.load_svg_file(svg)
            self.div2.appendChild(svgc.element)


    def _log(self, msg):
        self._talogs.value += str(msg) + '\n'
        # scroll textarea to bottom
        self._talogs.scrollTop = self._talogs.scrollHeight

        # svg_str = add_rounded_background2(_svg1, color)


class SvgElement(wpc.Component, tag_name='svg-element'):
    filename: str = wpc.attribute()
    _style: js.HTMLStyleElement = wpc.element()
    _div: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
        <style data-name="_style">
        :host {
  --svg-primary-color: #3574F0;
  --svg-secondary-color: #343a40; /* Darker Gray */
}
        </style>
        <div data-name="_div"></div>
        """

    def load_svg_file(self, file: Path):
        self.load_svg_str(file.read_text())

    def load_svg_str(self, svg: str):
        # self._div.innerHTML = add_rounded_background2(svg, _BLUE)
        # self._div.innerHTML = add_rounded_background2(svg, _BGRD)
        self._div.innerHTML = add_rounded_background2(svg, 'var(--svg-primary-color)')
        # r = js.document.createRange().createContextualFragment(svg_str)
        # self._div.appendChild(r)

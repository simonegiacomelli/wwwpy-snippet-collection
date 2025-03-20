import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)

from .d3js_plot.d3js_plot_component import D3jsPlotComponent #noqa


class Component1(wpc.Component, tag_name='component-1'):
    button1: js.HTMLButtonElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<hr>
<d3js-plot-component></d3js-plot-component>
"""

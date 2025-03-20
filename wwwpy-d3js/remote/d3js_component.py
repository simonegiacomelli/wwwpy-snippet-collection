import logging

import wwwpy.remote.component as wpc
from js import d3

logger = logging.getLogger(__name__)

from js import console, HTMLElement
from pyodide.ffi import create_proxy, to_js


class D3jsComponent(wpc.Component, tag_name='d3js-component'):
    cb1: HTMLElement = wpc.element()
    taLog: HTMLElement = wpc.element()
    root: HTMLElement = wpc.element()

    def init_component(self):
        # language=HTML
        self.element.innerHTML = """
            <h2>UseCase02_Widget</h2>
            <svg data-name="root"></svg>
            <br>
            <label>prevent default <input type='checkbox' data-name='cb1'></label> 
            <br>
            <textarea data-name="taLog" style='font-size: 0.7em' cols='60' rows='15'></textarea>
            """

    async def after_init_component(self):
        from .d3_helpers import newD3Group
        # https://observablehq.com/@d3/click-to-recenter-brush
        gBrush = newD3Group(d3.select(self.root))
        brush = d3.brushX().on("end", create_proxy(self.on_brush_end))
        brush.extent(to_js([[0, 0], [400, 100]]))
        gBrush \
            .call(brush) \
            .call(brush.move, to_js([40, 70])) \
            .lower()

    def on_brush_end(self, event, *args):
        console.log('on_brush_end', event)
        selection = event.selection
        console.log('on_brush_end selection', selection)
        self.taLog.value += f'on_brush_end selection {selection}\n'
        start = selection[0]
        end = selection[1]
        console.log(start + 1, end + 2)

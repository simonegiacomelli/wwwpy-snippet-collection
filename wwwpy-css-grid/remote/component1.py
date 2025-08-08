import re
from dataclasses import dataclass
from typing import Any, List, Tuple, cast

from pyodide.ffi import create_proxy
import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import eventlib

logger = logging.getLogger(__name__)


@dataclass
class Grid:
    rect: js.DOMRect
    vertical_corridors: List[Tuple[float, float]]
    horizontal_corridors: List[Tuple[float, float]]
    col_sizes: List[float]
    row_sizes: List[float]
    pad_top: float
    pad_left: float
    col_gap: float
    row_gap: float


class Component1(wpc.Component, tag_name='component-1'):
    textarea1: js.HTMLTextAreaElement = wpc.element()
    _container: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<style>
body {
  font-family: sans-serif;
}
.container > div {
  border-radius: 5px;
  padding: 10px;
  background-color: gray;
  border: 2px solid rgb(79 185 227);
}
.container {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 20px;
}

</style>    
<div class="container"  data-name="_container">
  <div>One</div>
  <div>Two</div>
  <div>Three</div>
  <div>Four</div>
  <div>Five</div>
  <div>Six</div>
  <div>Seven</div>
</div>
<textarea data-name="textarea1" placeholder="textarea1" rows="6" 
style="width: 100%; box-sizing: border-box; margin-top: 1em"></textarea>

"""

        cs = js.window.getComputedStyle(self._container)
        self.log_clear()
        self.log(f'grid-template-columns: {cs.gridTemplateColumns}')
        self.log(f'grid-template-rows: {cs.gridTemplateRows}')

        oc = cast(js.HTMLCanvasElement, js.document.createElement('canvas'))
        oc.style.position = 'absolute'
        oc.style.pointerEvents = 'none'
        oc.style.zIndex = '1'

        self.overlay_canvas = oc
        js.document.body.appendChild(oc)

        # state for hovered cell
        self.hovered_cell: Any = None

        # initial draw
        self.update_grid_overlay()

    def log_clear(self):
        self.textarea1.innerHTML = ''

    def log(self, msg):
        self.textarea1.innerHTML += f'{msg}\n'
        self.textarea1.scrollTop = self.textarea1.scrollHeight

    def calculate_grid(self):
        return calculate_grid(self._container)

    def update_grid_overlay(self):
        update_grid_overlay(self._container, self.overlay_canvas, self.hovered_cell)

    def _js_window__mousemove(self, e):
        self.hovered_cell = get_hovered_cell(e.clientX, e.clientY, self.calculate_grid())
        self.update_grid_overlay()

    def connectedCallback(self):
        eventlib.add_event_listeners(self)
        ro = js.ResizeObserver.new(create_proxy(lambda e, x: self.update_grid_overlay()))
        ro.observe(self._container)
        self._ro = ro

    def disconnectedCallback(self):
        eventlib.remove_event_listeners(self)
        # stop the ResizeObserver
        self._ro.disconnect()
        self._ro = None


# get bounds of a cell
def get_cell_bounds(g: Grid, col, row):
    x = g.pad_left
    y = g.pad_top
    for i in range(col): x += g.col_sizes[i] + g.col_gap
    for i in range(row): y += g.row_sizes[i] + g.row_gap
    return {'x': x, 'y': y, 'width': g.col_sizes[col], 'height': g.row_sizes[row]}


# compute which cell is under mouse
def get_hovered_cell(mx, my, g: Grid):
    x = mx - g.rect.left
    y = my - g.rect.top
    if x < g.pad_left or y < g.pad_top:
        return None
    col = -1
    cx = g.pad_left
    for i, size in enumerate(g.col_sizes):
        if x >= cx and x < cx + size:
            col = i
            break
        cx += size + g.col_gap
    row = -1
    cy = g.pad_top
    for i, size in enumerate(g.row_sizes):
        if y >= cy and y < cy + size:
            row = i
            break
        cy += size + g.row_gap
    return {'col': col, 'row': row} if col >= 0 and row >= 0 else None


def calculate_grid(container: js.HTMLElement) -> Grid:
    s = js.window.getComputedStyle(container)
    # parse CSS pixel values by stripping non-numeric chars
    parse = lambda x: float(re.sub(r'[^0-9.]', '', x)) if isinstance(x, str) else float(x)
    pad_top = parse(s.padding) or 0
    pad_left = parse(s.paddingLeft) or 0
    col_gap = parse(s.columnGap) or 0
    row_gap = parse(s.rowGap) or 0
    cols = [parse(x) for x in s.gridTemplateColumns.split()] or []
    rows = [parse(x) for x in s.gridTemplateRows.split()] or []

    def build(start, sizes, gap):
        pos = start
        lines = [(pos, pos)]
        for i, size in enumerate(sizes):
            pos += size
            end = pos + (gap if i < len(sizes) - 1 else 0)
            lines.append((pos, end))
            pos = end
        return lines

    rect = container.getBoundingClientRect()
    return Grid(
        rect=rect,
        vertical_corridors=build(pad_left, cols, col_gap),
        horizontal_corridors=build(pad_top, rows, row_gap),
        col_sizes=cols,
        row_sizes=rows,
        pad_top=pad_top,
        pad_left=pad_left,
        col_gap=col_gap,
        row_gap=row_gap
    )


# module-level overlay function
def update_grid_overlay(container, overlay_canvas, hovered_cell):
    g = calculate_grid(container)
    if not g:
        return
    c2d = cast(js.CanvasRenderingContext2D, overlay_canvas.getContext('2d'))
    rect = g.rect
    w, h = rect.width, rect.height
    # canvas width/height expects int
    overlay_canvas.width = int(w)
    overlay_canvas.height = int(h)
    overlay_canvas.style.top = f"{rect.top}px"
    overlay_canvas.style.left = f"{rect.left}px"
    c2d.clearRect(0, 0, w, h)

    c2d.strokeStyle = 'rgba(255,255,255,0.25)'
    c2d.lineWidth = 1
    for start, end in g.vertical_corridors:
        c2d.beginPath()
        c2d.moveTo(start, 0)
        c2d.lineTo(start, h)
        c2d.stroke()
        c2d.beginPath()
        c2d.moveTo(end, 0)
        c2d.lineTo(end, h)
        c2d.stroke()
    for start, end in g.horizontal_corridors:
        c2d.beginPath()
        c2d.moveTo(0, start)
        c2d.lineTo(w, start)
        c2d.stroke()
        c2d.beginPath()
        c2d.moveTo(0, end)
        c2d.lineTo(w, end)
        c2d.stroke()

    if hovered_cell:
        b = get_cell_bounds(g, hovered_cell['col'], hovered_cell['row'])
        c2d.strokeStyle = '#0f0'
        c2d.lineWidth = 3
        c2d.strokeRect(b['x'], b['y'], b['width'], b['height'])

from pyodide.ffi import create_proxy
import wwwpy.remote.component as wpc
import js
from typing import Any, cast

import logging

logger = logging.getLogger(__name__)


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

        # setup grid overlay canvas
        # type annotations for canvas and rendering context
        # cast created elements to specific types
        self.overlay_canvas: js.HTMLCanvasElement = cast(js.HTMLCanvasElement, js.document.createElement('canvas'))
        self.overlay_ctx: js.CanvasRenderingContext2D = cast(js.CanvasRenderingContext2D, self.overlay_canvas.getContext('2d'))
        js.document.body.appendChild(self.overlay_canvas)
        # canvas overlay styling
        self.overlay_canvas.style.position = 'absolute'
        self.overlay_canvas.style.pointerEvents = 'none'
        self.overlay_canvas.style.zIndex = '1'
        # state for hovered cell
        self.hovered_cell: Any = None

        # helper to calculate grid lines and sizes
        def calculate_grid():
            s = js.window.getComputedStyle(self._container)
            pad_top = float(s.paddingTop)
            pad_left = float(s.paddingLeft)
            col_gap = float(s.columnGap) if s.columnGap else 0
            row_gap = float(s.rowGap) if s.rowGap else 0
            cols = [float(x) for x in s.gridTemplateColumns.split()] or []
            rows = [float(x) for x in s.gridTemplateRows.split()] or []
            def build(start, sizes, gap):
                pos = start
                lines = [(pos, pos)]
                for i, size in enumerate(sizes):
                    pos += size
                    end = pos + (gap if i < len(sizes) - 1 else 0)
                    lines.append((pos, end))
                    pos = end
                return lines
            rect = self._container.getBoundingClientRect()
            return {'rect': rect, 'vert': build(pad_left, cols, col_gap), 'hor': build(pad_top, rows, row_gap), 'cols': cols, 'rows': rows, 'pad_top': pad_top, 'pad_left': pad_left, 'col_gap': col_gap, 'row_gap': row_gap}

        # compute which cell is under mouse
        def get_hovered_cell(mx, my, g):
            x = mx - g['rect'].left
            y = my - g['rect'].top
            if x < g['pad_left'] or y < g['pad_top']:
                return None
            col = -1
            cx = g['pad_left']
            for i, size in enumerate(g['cols']):
                if x >= cx and x < cx + size:
                    col = i
                    break
                cx += size + g['col_gap']
            row = -1
            cy = g['pad_top']
            for i, size in enumerate(g['rows']):
                if y >= cy and y < cy + size:
                    row = i
                    break
                cy += size + g['row_gap']
            return {'col': col, 'row': row} if col >= 0 and row >= 0 else None

        # get bounds of a cell
        def get_cell_bounds(g, col, row):
            x = g['pad_left']
            y = g['pad_top']
            for i in range(col): x += g['cols'][i] + g['col_gap']
            for i in range(row): y += g['rows'][i] + g['row_gap']
            return {'x': x, 'y': y, 'width': g['cols'][col], 'height': g['rows'][row]}

        # update grid overlay
        def update_grid_overlay():
            rect = self._container.getBoundingClientRect()
            w, h = rect.width, rect.height
            # canvas width/height expects int
            self.overlay_canvas.width = int(w)
            self.overlay_canvas.height = int(h)
            self.overlay_canvas.style.top = f"{rect.top}px"
            self.overlay_canvas.style.left = f"{rect.left}px"
            self.overlay_ctx.clearRect(0, 0, w, h)
            g = calculate_grid()
            # ensure grid data is available
            if not g:
                return
            vert = g['vert']
            hor = g['hor']
            self.overlay_ctx.strokeStyle = 'rgba(255,255,255,0.25)'
            self.overlay_ctx.lineWidth = 1
            for start, end in vert:
                self.overlay_ctx.beginPath()
                self.overlay_ctx.moveTo(start, 0)
                self.overlay_ctx.lineTo(start, h)
                self.overlay_ctx.stroke()
                self.overlay_ctx.beginPath()
                self.overlay_ctx.moveTo(end, 0)
                self.overlay_ctx.lineTo(end, h)
                self.overlay_ctx.stroke()
            for start, end in hor:
                self.overlay_ctx.beginPath()
                self.overlay_ctx.moveTo(0, start)
                self.overlay_ctx.lineTo(w, start)
                self.overlay_ctx.stroke()
                self.overlay_ctx.beginPath()
                self.overlay_ctx.moveTo(0, end)
                self.overlay_ctx.lineTo(w, end)
                self.overlay_ctx.stroke()
            # highlight hovered cell
            if self.hovered_cell:
                b = get_cell_bounds(g, self.hovered_cell['col'], self.hovered_cell['row'])
                self.overlay_ctx.strokeStyle = '#0f0'
                self.overlay_ctx.lineWidth = 3
                self.overlay_ctx.strokeRect(b['x'], b['y'], b['width'], b['height'])

        self.update_grid_overlay = update_grid_overlay
        # mouse move and resize listeners
        # mouse move: update hovered cell and overlay
        def on_mousemove(e):
            self.hovered_cell = get_hovered_cell(e.clientX, e.clientY, calculate_grid())
            update_grid_overlay()
        js.document.addEventListener('mousemove',  create_proxy( on_mousemove))
        if hasattr(js.window, 'ResizeObserver'):
            ro = js.ResizeObserver.new(create_proxy(lambda e: update_grid_overlay()))
            ro.observe(self._container)
        else:
            js.window.addEventListener('resize', create_proxy(lambda e: update_grid_overlay()))
        # initial draw
        update_grid_overlay()

    def log_clear(self):
        self.textarea1.innerHTML = ''

    def log(self, msg):
        self.textarea1.innerHTML += f'{msg}\n'
        self.textarea1.scrollTop = self.textarea1.scrollHeight
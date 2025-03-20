import logging

import wwwpy.remote.component as wpc
from js import d3
from wwwpy.common.asynclib import create_task_safe

from remote.d3_helpers import newD3Group
from remote.datachart_args import ApiDatachartCsvDataResponse, ApiDatachartCsvInfoResponse, ValueColumn, ColumnValues
from remote.itertools import associateby

logger = logging.getLogger(__name__)

from js import console, HTMLElement

from js import d3, console, HTMLElement, Date
from pyodide.ffi import create_proxy, to_js
from pydantic import BaseModel

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Iterable


class D3jsPlotComponent(wpc.Component, tag_name='d3js-plot-component'):
    taLog: HTMLElement = wpc.element()
    root: HTMLElement = wpc.element()

    def init_component(self):
        # language=HTML
        self.element.innerHTML = """
            <svg data-name="root" style="width: 500px; height: 80px"></svg>
            <br>
            <textarea data-name="taLog" style='font-size: 0.7em' cols='60' rows='15'></textarea>
            """

    async def after_init_component(self):
        try:
            await self._after_init_internal()
        except Exception as e:
            self.taLog.value += f'after_init_component {e}\n'

    async def _after_init_internal(self):
        gBrush = newD3Group(d3.select(self.root))
        gContent = gBrush

        data: ApiDatachartCsvDataResponse = json_to_instance(ApiDatachartCsvDataResponse, 'data-2041.json')
        data_dict = associateby(data.column_values, lambda c: c.name)
        info: ApiDatachartCsvInfoResponse = json_to_instance(ApiDatachartCsvInfoResponse, 'info.json')
        columns: Dict[str, ValueColumn] = {}
        logger.debug(f'info.columns {info.columns}')
        for col in info.columns:
            logger.debug(f'col.name {col.name}')
            vals: ColumnValues = data_dict.get(col.name, None)
            if vals is not None:
                colval = ValueColumn(values=vals.values, **vars(col))
                columns[col.name] = colval
                ColumnPlot(gContent, colval, data.timestamp_values, []).render()

        brush = d3.brushX().on("end", create_proxy(self.on_brush_end))
        brush.extent(to_js([[0, 0], [500, 80]]))
        gBrush \
            .call(brush) \
            .call(brush.move, to_js([40, 70])) \
            .lower()

    def on_brush_end(self, event, *args):
        selection = event.selection
        self.taLog.value += f'on_brush_end selection {selection}\n'


def json_to_instance(response, data_json):
    text = (Path(__file__).parent / data_json).read_text()
    args = json.loads(text)
    resp = response(**args)
    return resp


def filter_out_none(x: List[datetime], y: List[object]):
    return zip(*((x1, y1) for x1, y1 in zip(x, y) if y1 is not None))


def datetime_to_jsdate(d: datetime) -> Date:
    return Date.new(d.isoformat())


def to_js_datetime(iterable: Iterable[datetime]) -> List[Date]:
    return list(map(datetime_to_jsdate, iterable))


class ColumnPlot:
    def __init__(
            self,
            gContent,
            column: ValueColumn,
            x_all_values: List[datetime],
            label_columns: List[ValueColumn]
    ):
        self.gContent = gContent
        self.column = column
        self.x_all_values = x_all_values
        self.label_columns = label_columns
        self.x_values, self.y_values = filter_out_none(x_all_values, column.values)

    def render(self):
        geo = SimpleNamespace()
        geo.y_range = [400, 0]
        geo.x_range = [0, 600]
        y_scale = d3.scaleLinear() \
            .domain(d3.extent(to_js(self.y_values))) \
            .range(to_js(geo.y_range))

        x_scale = d3.scaleTime() \
            .domain(d3.extent(to_js_datetime(self.x_all_values))) \
            .range(to_js(geo.x_range))

        def x_mapper(tup, *args):
            # console.log('tup', str(tup), 'args', str(args))
            x: datetime
            index, x = tup
            y = self.y_values[index]
            # console.log('index', index, 'x', x, 'y', y)
            point = Point(
                x=x,
                y=y,
                x_scaled=x_scale(datetime_to_jsdate(x)),
                y_scaled=y_scale(y),
            )
            return point

        points: List[Point] = list(map(x_mapper, enumerate(self.x_values)))
        d: Point
        self.gContent \
            .append('g') \
            .selectAll('myCircles') \
            .data(to_js(points)) \
            .enter() \
            .append("circle") \
            .attr("fill", lambda d, *args: self.column.color) \
            .attr("stroke", "none") \
            .attr("cx", lambda d, *args: d.x_scaled) \
            .attr("cy", lambda d, *args: d.y_scaled) \
            .attr("r", 3) \
            .attr('fill-opacity', 0.7)

        # self.gContent \
        #     .append('g') \
        #     .append('path') \
        #     .datum(to_js(data)) \
        #     attr()


class Point(BaseModel):
    x: datetime
    y: float

    x_scaled: float
    y_scaled: float

    # color: str

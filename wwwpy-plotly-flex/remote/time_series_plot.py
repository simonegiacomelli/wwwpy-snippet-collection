"""Component to plot time series data."""

import logging
from datetime import timedelta

import js
import pandas as pd
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js
from wwwpy.remote.jslib import script_load_once

__all__ = ["TimeSeriesPlot"]

from common.decorators import throttle, debounce

logger = logging.getLogger(__name__)


class TimeSeriesPlot(wpc.Component, tag_name="time-series-plot"):
    plotDiv: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
            <div data-name="plotDiv" style="width: auto; height:400px; margin:auto;"></div>       
        """
        self._data: pd.DataFrame | None = None

    async def after_init_component(self):
        await script_load_once("https://cdn.plot.ly/plotly-3.0.0.min.js", charset="utf-8")
        self._generate_plot()
        # Automatically re-generate the plot whenever the browser window is resized.
        js.ResizeObserver.new(create_proxy(self._resize)).observe(self.plotDiv)

    @debounce(timedelta(milliseconds=300))
    def _resize(self, entries, observer):
        """Re-generate plot after resizing its container."""
        self._generate_plot()

    def update_plot(self, data: pd.DataFrame | None):
        """Update plot content.

        Arguments:
            data: Data to plot as dataframe with index of dtype `pd.Timestamp`.
        """
        self._data = data
        self._generate_plot()

    def _generate_plot(self):
        """Generate Plotly plot."""
        if self._data is None or self._data.empty:
            return self._plot_no_data()

        layout = {
            "xaxis": {"range": [self._data.index[0], self._data.index[-1]]},
            "yaxis": {"title": "Title1"},
            "title": "Time Series Data",
        }

        traces = [
            {
                "x": [_to_javascript_date(idx) for idx in self._data.index],
                "y": self._data[cname].tolist(),
                "mode": "lines",
                "name": cname,
            } for cname in self._data.columns.tolist()
        ]

        js.Plotly.newPlot(self.plotDiv, dict_to_js(traces), dict_to_js(layout))

    def _plot_no_data(self):
        """Display a 'No Data Available' label without axes."""
        layout = {
            "xaxis": {"showgrid": False, "zeroline": False, "visible": False},
            "yaxis": {"showgrid": False, "zeroline": False, "visible": False},
            "annotations": [
                {
                    "text": "No Data Available",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 20}
                }
            ]
        }

        js.Plotly.newPlot(self.plotDiv, [], dict_to_js(layout))


def _to_javascript_date(ts: pd.Timestamp):
    return str(ts).replace(' ', 'T')

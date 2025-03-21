import wwwpy.remote.component as wpc
import js

import logging
from .time_series_plot import TimeSeriesPlot

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):

    def init_component(self):
        # language=html
        self.element.innerHTML = """<div>component-1</div>
<hr>
<div style="display: flex; gap: 10px">
    <time-series-plot data-name='time_series_plot_0' style="flex: 1;"></time-series-plot>
    <time-series-plot data-name='time_series_plot_1' style="flex: 1;"></time-series-plot>
</div>
<hr>
"""

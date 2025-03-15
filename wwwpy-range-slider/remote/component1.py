import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    input1: js.HTMLInputElement = wpc.element()
    _slider1: js.HTMLInputElement = wpc.element()
    _div1: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<style>

.slider {
  -webkit-appearance: none;
  width: 100%;
  height: 25px;
  background: #d3d3d3;
  outline: none;
  opacity: 0.7;
  -webkit-transition: .2s;
  transition: opacity .2s;
}

.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 25px;
  height: 25px;
  background: #04AA6D;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 25px;
  height: 25px;
  background: #04AA6D;
  cursor: pointer;
}
</style>



<h1>Custom Range Slider</h1>

<div class="slidecontainer">
  <input data-name='_slider1' type="range" min="1" max="100" value="50" class="slider">
<div data-name="_div1">move the slider to get the value</div>
</div>

"""

    async def _slider1__input(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} '
                     f'_slider1.value={self._slider1.value}')
        self._div1.innerHTML = f'{self._slider1.value}'
    

import inspect
import wwwpy.remote.component as wpc
import js

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
<textarea data-name="textarea1" placeholder="textarea1" rows="6" wrap="off" 
style="width: 100%; box-sizing: border-box; margin-top: 1em"></textarea>

"""

        cs = js.window.getComputedStyle(self._container)
        self.log_clear()
        self.log(f'grid-template-columns: {cs.gridTemplateColumns}')
        self.log(f'grid-template-rows: {cs.gridTemplateRows}')
        # cs.gridTemplateRows

    def log_clear(self):
        self.textarea1.innerHTML = ''

    def log(self, msg):
        self.textarea1.innerHTML += f'{msg}\n'
        self.textarea1.scrollTop = self.textarea1.scrollHeight
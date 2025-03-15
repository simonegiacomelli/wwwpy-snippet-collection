import inspect
import wwwpy.remote.component as wpc
import js

import logging

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _show_btn: js.HTMLButtonElement = wpc.element()
    _dialog: js.HTMLDialogElement = wpc.element()
    _output: js.HTMLOutputElement = wpc.element()
    _select: js.HTMLSelectElement = wpc.element()
    _show_dialog_btn: js.HTMLButtonElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<dialog data-name="_dialog">
  <form>
    <p>
      <label>
        Favorite animal:
        <select data-name="_select">
          <option value="default">Choose…</option>
          <option>Brine shrimp</option>
          <option>Red panda</option>
          <option>Spider monkey</option>
        </select>
      </label>
    </p>
    <div>
      <button formmethod="dialog" value="cancel" data-name="_cancel">Cancel</button>
      <button value="default" data-name="_confirm">Confirm</button>
    </div>
  </form>
</dialog>
<p>
  <button id="showDialog" data-name="_show_btn">dialog.show()</button>
<button data-name="_show_dialog_btn">dialog.showModal()</button>
</p>
<output data-name="_output"></output>
"""

    async def _show_btn__click(self, event):
        self._dialog.show()

    async def _show_dialog_btn__click(self, event):
        self._dialog.showModal()

    def _dialog__close(self, event):
        default = self._dialog.returnValue == 'default'
        self._output.value = 'No return value.' if default else f'ReturnValue: {self._dialog.returnValue}.'
    
    def _confirm__click(self, event):
        event.preventDefault()
        self._dialog.close(self._select.value)
    

import inspect
import logging
import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


class UcToggleSwitchComponent(wpc.Component, tag_name='uc-toggle-switch'):
    checked: str = wpc.attribute()
    text: str = wpc.attribute()
    _checkbox: js.HTMLInputElement = wpc.element()
    _text: js.HTMLElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        self.element.shadowRoot.innerHTML = """<style>
    :host {
        --width: 2.5em;
        --height: 1.42em;
        --offset: 0.17em;
        --slider-size: calc(var(--height) - 0.33em);
    }
    .switch {
        position: relative;
        display: inline-block;
        width: var(--width);
        height: var(--height);
    }
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: var(--slider-size);
        width: var(--slider-size);
        left: var(--offset);
        bottom: var(--offset);
        background-color: white;
        transition: .4s;
    }
    input:checked + .slider {
        background-color: #2196F3;
    }
    input:focus + .slider {
        box-shadow: 0 0 1px #2196F3;
    }
    input:checked + .slider:before {
        transform: translateX(calc(var(--width) - var(--height)));
    }
    .slider.round {
        border-radius: var(--height);
    }
    .slider.round:before {
        border-radius: 50%;
    }
    .toggle-text {
        margin-left: 0.5em;
        vertical-align: middle;
        font-size: 1em;
        cursor: pointer;
    }
</style>
<label class="switch">
    <input type="checkbox" data-name="_checkbox">
    <span class="slider round"></span>
</label>
<span class="toggle-text" data-name="_text"></span>
"""
        self._read_attribute_changed()

    def attributeChangedCallback(self, name: str, oldValue: str, newValue: str):
        self._read_attribute_changed()

    def _read_attribute_changed(self):
        self._checkbox.checked = self.checked_bool
        self._text.textContent = self.text if self.text is not None else ""

    def _checkbox__change(self, event):
        self.checked_bool = self._checkbox.checked

    def _text__click(self, event):
        self.checked_bool = not self.checked_bool
        self._read_attribute_changed()
        for event_name in ['change', 'input']:
            self.element.dispatchEvent(js.Event.new(event_name, dict_to_js({"checked": self._checkbox.checked})))

    @property
    def checked_bool(self) -> bool:
        return self.element.hasAttribute('checked')

    @checked_bool.setter
    def checked_bool(self, value: bool):
        if value:
            self.element.setAttribute('checked', '')
        else:
            self.element.removeAttribute('checked')
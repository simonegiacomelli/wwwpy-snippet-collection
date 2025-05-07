from __future__ import annotations

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js
from wwwpy.remote.component import get_component


class AccordionContainer(wpc.Component, tag_name='wwwpy-accordion-container'):
    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        self.element.shadowRoot.innerHTML = '<slot></slot>'

    @property
    def sections(self) -> list[AccordionSection]:
        return [
            get_component(child) for child in self.element.children
            if child.tagName.lower() == 'wwwpy-accordion-section'
        ]

    def collapse_all(self):
        for section in self.sections:
            section.expanded = False

    def expand_all(self):
        for section in self.sections:
            section.expanded = True


class AccordionSection(wpc.Component, tag_name='wwwpy-accordion-section'):
    _header_container: js.HTMLElement = wpc.element()
    _panel_container: js.HTMLElement = wpc.element()
    _expanded: bool

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """<style>
    .panel-container {
        display: grid;
        transition: grid-template-rows 300ms ease-in-out;
    }
</style>
<slot data-name="_header_container">Header</slot>
<div data-name="_panel_container" class="panel-container" >
    <div style="overflow: hidden">
        <slot name="panel">Panel</slot>
    </div>
</div>
"""
        self._expanded = False
        self.expanded = False

    def _header_container__click(self, event):
        self.toggle(True)

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, value):
        new_value = bool(value)
        if self._expanded == new_value:
            return
        self._expanded = new_value
        self._panel_container.style.gridTemplateRows = '1fr' if self._expanded else '0fr'

    def toggle(self, emit_event=False):
        self.expanded = not self.expanded
        if not emit_event:
            return
        event_dict = dict_to_js({'bubbles': True, 'detail': {'section': self.element, 'expanded': self._expanded}})
        event = js.CustomEvent.new('accordion-toggle', event_dict)
        self.element.dispatchEvent(event)

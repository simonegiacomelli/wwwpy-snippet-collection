from __future__ import annotations

import inspect

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging

from . import element_selector  # import to register the element-selector component
from .element_selector import ElementSelector

logger = logging.getLogger(__name__)


class MainComponent(wpc.Component, tag_name='main-component'):
    """Main component to showcase the use of the ElementSelector component."""

    # Elements
    canvas: js.HTMLDivElement = wpc.element()
    element_selector: ElementSelector = wpc.element()

    def init_component(self):
        """Initialize the component"""
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
        <style>
            :host {
                display: block;
                font-family: sans-serif;
                padding: 20px;
            }
            
            h1 {
                margin-bottom: 10px;
            }
            
            .content-area {
                position: relative;
                border: 1px dashed #ccc;
                padding: 20px;
                margin-bottom: 20px;
            }
            
            .element {
                padding: 15px;
                margin: 10px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                cursor: pointer;
            }
            
            .flex-container {
                display: flex;
                justify-content: space-between;
            }
            
            .narrow {
                width: 30%;
            }
            
            .wider {
                width: 60%;
            }
        </style>
        
        <h1>Selection Highlight Demo</h1>
        <p>Click on any element below to select it. A highlight and toolbar will appear without changing the layout.</p>
        <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
        
        <div class="content-area" data-name="canvas" id="canvas">
            <div class="element" id="element1">Element 1</div>
            <div class="element" id="element2">Element 2</div>
            <div class="element" id="element3">
                Element 3 with some longer content to show how the highlight adapts to different sizes.
            </div>
            <div class="flex-container">
                <div class="element narrow" id="element4">Element 4 (narrow)</div>
                <div class="element wider" id="element5">Element 5 (wider)</div>
            </div>
        </div>
        
        <!-- Our custom element for selection highlighting -->
        <element-selector data-name="element_selector" id="element-selector"></element-selector>
        """
        self._mouse_move = create_proxy(self._mouse_move)

    def connectedCallback(self):
        # connect the mouse move
        js.document.addEventListener('mousemove', self._mouse_move)

    def disconnectedCallback(self):
        # disconnect the mouse move
        js.document.removeEventListener('mousemove', self._mouse_move)

    def _mouse_move(self, event: js.MouseEvent):
        path = event.composedPath()
        js.console.log(f'Mouse move event: {event.clientX}, {event.clientY}', path, event.target, event)
        el = path[0] if path and len(path) > 0 else event.target

        self.element_selector.set_selected_element(el)

    def element_selector__toolbar_action(self, e):
        # Display an alert with the action and element ID
        detail = e.detail
        js.window.alert(f"Action: {detail.action} on {detail.element.id}")

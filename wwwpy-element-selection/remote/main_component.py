from __future__ import annotations

import inspect
from typing import Optional

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy, JsProxy
from wwwpy.common.designer import code_strings, html_locator
from wwwpy.common.designer.element_path import ElementPath, Origin
from wwwpy.remote import dict_to_js

import logging

from wwwpy.remote.designer import element_path
from wwwpy.remote.designer.helpers import _element_path_lbl

# from wwwpy.remote.designer.ui.property_editor import _rebase_element_path_to_origin_source

from . import element_selector  # import to register the element-selector component
from .element_selector import ElementSelector

logger = logging.getLogger(__name__)


class MainComponent(wpc.Component, tag_name='main-component'):
    f"""Main component to showcase the use of the ElementSelector component."""

    # Elements
    element_selector: ElementSelector = wpc.element()
    _on_mouse_move: js.HTMLInputElement = wpc.element()
    ele1: js.HTMLDivElement = wpc.element()
    cont1: js.HTMLDivElement = wpc.element()

    def init_component(self):
        f"""Initialize the component"""
        # self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # self.element.shadowRoot.innerHTML = """
        # language=html
        self.element.innerHTML = """
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
        <input data-name="_on_mouse_move" placeholder="input1" type="checkbox" checked>
        <p>Click on any element below to select it. A highlight and toolbar will appear without changing the layout.</p>
        
        <inner-component></inner-component>

        <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
        
        <div class="content-area" data-name="cont1">
            <div class="element" id="element1" data-name="ele1">Element 1</div>
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
        self._mouse_click = create_proxy(self._mouse_click)

    def connectedCallback(self):
        js.document.addEventListener('mousemove', self._mouse_move)
        js.document.addEventListener('click', self._mouse_click)

    def disconnectedCallback(self):
        js.document.removeEventListener('mousemove', self._mouse_move)
        js.document.removeEventListener('click', self._mouse_click)

    def _mouse_move(self, event: js.MouseEvent):
        if not self._on_mouse_move.checked:
            return
        self._change_selection_from_event(event)

    def _mouse_click(self, event: js.MouseEvent):
        if event.target == self._on_mouse_move:
            return
        self._on_mouse_move.checked = False
        self._change_selection_from_event(event)

    def _change_selection_from_event(self, event):
        path = event.composedPath()
        el = path[0] if path and len(path) > 0 else event.target
        js.console.log(f'change selection: {event.clientX}, {event.clientY}', path, event)

        self._set_selection(el)

    def _set_selection(self, el):
        js.console.log(f'_set_selection to el:', el)
        self.element_selector.set_selected_element(el)
        ep_live = element_path.element_path(el)
        logger.debug(f'Element path live: {ep_live}')
        ep_source = _rebase_element_path_to_origin_source(ep_live)
        logger.debug(f'Element path source: {ep_source}')
        message = 'ep_source is none' if ep_source is None else f'Selection: {_element_path_lbl(ep_source)}'
        logger.debug(message)
        if ep_source is not None:
            from wwwpy.remote.designer.ui.dev_mode_component import DevModeComponent
            tb = DevModeComponent.instance.toolbox
            tb._toolbox_state.selected_element_path = ep_live
            tb._restore_selected_element_path()


    def element_selector__toolbar_action(self, e):
        # Display an alert with the action and element ID
        detail = e.detail
        # js.window.alert(f"Action: {detail.action} on {detail.element.id}")
        parent = None
        if detail.action == 'Move up':
            parent = next_element(detail.element, 'up')
        if detail.action == 'Move down':
            parent = next_element(detail.element, 'down')
        if detail.action == 'Parent':
            parent = parent_element(detail.element)

        if parent:
            self._set_selection(parent)



class InnerComponent(wpc.Component, tag_name='inner-component'):
    inner_button: js.HTMLButtonElement = wpc.element()
    div_root2: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """<div data-name="div_root2">
    <h2>Inner Component</h2>
    <p>This is an inner component. Click on the button below to select it.</p>
    <button data-name="inner_button">Inner Button</button>
</div>"""



def parent_element(element: js.HTMLElement) -> js.HTMLElement | None:
    if element_path.is_instance_of(element, js.ShadowRoot):
        element = element.host

    element = element.parentNode

    if element_path.is_instance_of(element, js.ShadowRoot):
        element = element.host

    return element

def next_element(element: js.HTMLElement, up_down:str) -> js.HTMLElement | None:
    if element_path.is_instance_of(element, js.ShadowRoot):
        element = element.host

    if up_down == 'up':
        if element.previousElementSibling is None:
            element = element.parentNode
        else:
            element = element.previousElementSibling
    elif up_down == 'down':
        if element.nextElementSibling is None:
            element = element.parentNode
        else:
            element = element.nextElementSibling

    if element_path.is_instance_of(element, js.ShadowRoot):
        element = element.host

    return element

def _rebase_element_path_to_origin_source(ep: ElementPath) -> Optional[ElementPath]:
    """This is similar to rebase_path dumb because we use indexes alone.
    This rebase from Origin.live to Origin.source
    """
    logger.debug(f'_rebase_element_path_to_origin_source {ep}')
    if not ep:
        return None
    if ep.origin == Origin.source:
        return ep

    html = code_strings.html_from(ep.class_module, ep.class_name)
    if not html:
        logger.debug(f'Cannot find html for {ep.class_module}.{ep.class_name}')
        return None

    cst_node = html_locator.locate_node(html, ep.path)
    if cst_node is None:
        logger.debug(f'Cannot find node for {ep.path} in {ep.class_module}.{ep.class_name}')
        return None

    node_path = html_locator.node_path_from_leaf(cst_node)
    ep_source = ElementPath(ep.class_module, ep.class_name, node_path, Origin.source)
    return ep_source

from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from pyodide.ffi import create_proxy
from wwwpy.remote import dict_to_js

import logging

logger = logging.getLogger(__name__)


class MainComponent(wpc.Component, tag_name='main-component'):
    content_area: js.HTMLDivElement = wpc.element()
    element_selector: js.HTMLElement = wpc.element()  # Reference to our element-selector

    def init_component(self):
        """Initialize the main component"""
        self.element.innerHTML = """
            <h1>Selection Highlight Demo (Python Version)</h1>
            <p>Click on any element below to select it. A highlight and toolbar will appear without changing the layout.</p>
            
            <div class="content-area" id="canvas" data-name="content_area">
                <div class="element" id="element1">Element 1</div>
                <div class="element" id="element2">Element 2</div>
                <div class="element" id="element3">
                    Element 3 with some longer content to show how the highlight adapts to different sizes.
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div class="element" id="element4" style="width: 30%;">Element 4 (narrow)</div>
                    <div class="element" id="element5" style="width: 60%;">Element 5 (wider)</div>
                </div>
            </div>
            
            <!-- Attach our custom element for selection highlighting -->
            <element-selector data-name="element_selector"></element-selector>
            
            <style>
                /* Core container styles */
                body {
                    font-family: sans-serif;
                    padding: 20px;
                }
                
                .content-area {
                    position: relative;
                    border: 1px dashed #ccc;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                
                /* Selectable elements */
                .element {
                    padding: 15px;
                    margin: 10px;
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    cursor: pointer;
                }
            </style>
        """

    async def after_init_component(self):
        """Set up after initialization"""
        # Get all elements with the 'element' class
        elements = self.content_area.querySelectorAll('.element')

        # Handle element selection
        for element in elements:
            element.addEventListener('click', create_proxy(
                lambda e: self._handle_element_click(e)
            ))

        # Handle clicks outside to deselect
        js.document.addEventListener('click', create_proxy(
            lambda e: self._handle_document_click(e)
        ))

        # Handle toolbar actions
        self.element_selector.addEventListener('toolbar-action', create_proxy(
            lambda e: self._handle_toolbar_action(e)
        ))

    def _handle_element_click(self, e):
        """Handle clicks on the elements"""
        e.stopPropagation()
        # Pass the clicked element to the selector component
        element_selector = js.document.querySelector('element-selector')
        element_selector.selected_element = e.currentTarget

    def _handle_document_click(self, e):
        """Handle clicks outside elements to deselect"""
        # Check if the click was on an element or inside the element-selector
        if not (e.target.closest('.element') or e.target.closest('element-selector')):
            element_selector = js.document.querySelector('element-selector')
            element_selector.selected_element = None

    def _handle_toolbar_action(self, e):
        """Handle toolbar actions"""
        # Display an alert with the action and element ID
        js.window.alert(f"Action: {e.detail.action} on {e.detail.element.id}")
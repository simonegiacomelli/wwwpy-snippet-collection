from remote.component2 import Component2
import inspect
import wwwpy.remote.component as wpc
import js

import logging

# from .custom_tree import CustomTreeDemo
from .custom_tree_ui import CustomTreeDemo
from . import comp_structure  # noqa

logger = logging.getLogger(__name__)
x = CustomTreeDemo


class Component1(wpc.Component, tag_name='component-1'):
    a1: js.HTMLAnchorElement = wpc.element()
    textarea1: js.HTMLTextAreaElement = wpc.element()
    div1: js.HTMLDivElement = wpc.element()
    _container: js.HTMLDivElement = wpc.element()
    hr1: js.HTMLHRElement = wpc.element()
    hr2: js.HTMLHRElement = wpc.element()
    div2: js.HTMLDivElement = wpc.element()
    component2a: Component2 = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<wwwpy-comp-structure-2></wwwpy-comp-structure-2>
<br>

<component-2 data-name="component2a"></component-2><div data-name="div2">div2</div><hr data-name="hr1">
<hr data-name="hr2"></hr></hr><custom-tree-demo></custom-tree-demo>        
<hr>        
<style>
    .grid-item {
        background: linear-gradient(45deg, #e3f2fd, #bbdefb);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #1565c0;
        border: 3px solid #90caf9;
    }
</style>
<div>component-1
    <textarea data-name="textarea1" placeholder="textarea1"
              rows="6" wrap="off" style="width: 100%; font-size: x-small; box-sizing: border-box"></textarea>

    <div data-name="div1"
         style="    
         
         display: grid;   
         grid-template-columns: repeat(3, 1fr);    
         grid-template-rows: repeat(2, 1fr);     
         gap: 10px; 
         border: 2px solid red">
        <div class="grid-item">Item 1</div>
        <div class="grid-item">Item 2</div>
        <div class="grid-item">Item 3</div>
        <div class="grid-item">Item 4</div>
        <div class="grid-item">Item 5</div>
        <div class="grid-item">Item 6</div>
        <div class="grid-item">Item 7</div>
        <div class="grid-item">Item 8</div>
        <div class="grid-item">Item 9
            
        </div>
    </div>
</div>

<hr>
<div class="grid-container" id="grid-container"
     style="
     box-sizing: border-box;  
     border: 1px solid red;
     display: grid;
     grid-template-columns: 1fr 2fr 1fr;
     grid-template-rows: 1fr 1fr 1fr;
     column-gap: 10px;
     row-gap: 20px;
     place-content: stretch;
     place-items: stretch;
     width: 182px;
     height: 132px;
     overflow: auto;
    " data-name="_container">

    <div class="grid-item" contenteditable=''></div>
    <div class="grid-item" contenteditable=""></div>
    <div class="grid-item" contenteditable=""></div>
    <div class="grid-item" contenteditable="" style="grid-column: 2/3; grid-row: 3/4">  1</div>
    <div class="grid-item" contenteditable="" style="grid-column: 2/4; grid-row: 3/4; opacity: 0.3">2</div>
  



</div>

<div class="grid-item" contenteditable=""></div>
<div class="grid-item" contenteditable=""></div>
<div class="grid-item" contenteditable=""></div>
<div class="grid-item" contenteditable=""></div>

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

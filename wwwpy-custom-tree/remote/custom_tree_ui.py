from __future__ import annotations
import inspect

import logging
from functools import cached_property

import js
import wwwpy.remote.component as wpc
from pyodide.ffi import create_proxy
from wwwpy.common.collectionlib import ObservableList
from wwwpy.common.designer.ui.icons.all_icons import AllIcons
from wwwpy.remote import dict_to_js
from wwwpy.remote.component import Component
from wwwpy.remote.designer.ui.svg_icon import SvgIcon
from wwwpy.remote.jslib import is_instance_of

from remote.tree_node import Node, NodeList

logger = logging.getLogger(__name__)


def _default_template_make() -> js.Element | None:
    # language=html

    return js.document.createRange().createContextualFragment("""
    <template data-name="_default_template">
        <div data-name="_e_node">
            <div class="tree-node-header" data-name="_e_header">
                <span class="tree-node-chevron" data-name="_e_chevron">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 11.5L9.5 8L6 4.5" stroke="#B4B8BF" stroke-linecap="round"/>
                    </svg>
                </span>
                <span class="tree-node-text" >
                    <span data-name="_e_text"></span>
                    <span data-name="_e_additional"></span>
                </span>
                
            </div>
            <div class="tree-node-children" data-name="_e_children"></div>
        </div>
    </template>
""").firstElementChild


_default_template: js.HTMLTemplateElement = _default_template_make()  # noqa


class UiNode(Node, ObservableList):

    def __init__(self):
        super().__init__()
        self._children: list[UiNode] = self
        self._parent = None
        frag = _default_template.content.cloneNode(True)
        self.frag = frag
        self._e_node: js.HTMLElement = frag.querySelector('[data-name="_e_node"]')
        self._e_header: js.HTMLElement = frag.querySelector('[data-name="_e_header"]')
        self._e_chevron: js.HTMLElement = frag.querySelector('[data-name="_e_chevron"]')
        self._e_children: js.HTMLElement = frag.querySelector('[data-name="_e_children"]')
        self._e_text: js.HTMLElement = frag.querySelector('[data-name="_e_text"]')
        self._e_additional: js.HTMLElement = frag.querySelector('[data-name="_e_additional"]')
        # self.expanded = False
        self._children_changed()

        def on_toggle(e):
            e.stopPropagation()
            self.toggle()
            if self.expanded and len(self._children) > 0:
                self._e_node.scrollIntoView(dict_to_js({'block': 'nearest', 'inline': 'nearest'}))

        self._e_chevron.addEventListener('click', create_proxy(on_toggle))

        def on_click(ev):
            self.root().deselect_all()
            self.selected = not self.selected

        self._e_header.addEventListener('click', create_proxy(on_click))

    @property
    def level(self) -> int:
        return self.parent.level + 1 if self.parent else -1

    @property
    def children(self) -> list[UiNode]:
        return self._children

    @property
    def parent(self) -> UiNode | None:
        return self._parent

    @parent.setter
    def parent(self, value: NodeList | None):
        self._parent = value
        logger.debug(f'Setting parent of {self.text} to {value.text} level={self.level}')
        self._e_header.style.paddingLeft = f"{self.level * 20 + 8}px"

    def set_surrogate_root(self):
        self._e_header.style.display = 'none'
        self.expanded = True

    def selected_nodes(self) -> set[Node]:
        result = {self} if self.selected else set()
        for c in self._children:
            result |= c.selected_nodes()
        return result

    def deselect_all(self, recursive: bool = True):
        self.selected = False
        if recursive:
            for c in self._children:
                c.deselect_all(recursive)

    def toggle(self):
        self.expanded = not self.expanded

    @property
    def text(self) -> str:
        return self._e_text.textContent

    @text.setter
    def text(self, value: str):
        self._e_text.textContent = value

    @property
    def backgroundColor(self) -> str:
        return self._e_header.style.backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, value: str):
        self._e_header.style.backgroundColor = value

    @property
    def expanded(self) -> bool:
        return self._e_children.style.display != 'none'

    @expanded.setter
    def expanded(self, value: bool):
        self._e_children.style.display = '' if value else 'none'
        self._e_chevron.style.transform = 'rotate(90deg)' if value else ''

    @property
    def selected(self) -> bool:
        return self._e_header.classList.contains('selected')

    @selected.setter
    def selected(self, value: bool):
        if value:
            self._e_header.classList.add('selected')
        else:
            self._e_header.classList.remove('selected')

    @cached_property
    def dom_node(self):
        return self.frag

    def _children_changed(self):
        has_kids = len(self._children) > 0
        self._e_chevron.style.visibility = '' if has_kids else 'hidden'
        if has_kids:
            self._e_children.classList.add('tree-node-children')

    def _item_added(self, item, index):
        if not isinstance(item, UiNode):
            logger.error(f'Expected UiNode, got {type(item)}')
            return
        item.parent = self
        self._e_children.appendChild(item.dom_node)
        self._children_changed()

    def _item_removed(self, item, index):
        if not isinstance(item, UiNode):
            logger.error(f'Expected UiNode, got {type(item)}')
            return
        item.parent = None
        self._e_children.removeChild(item.dom_node)
        self._children_changed()

    def additional(self, add: js.Element | Component):
        if isinstance(add, Component):
            add = add.element

        if not is_instance_of(add, js.Element):
            logger.error(f'Expected js.Element or Component, got {type(add)}')
            return

        self._e_additional.appendChild(add)


class CustomTreeUI(wpc.Component, tag_name='custom-tree-ui'):
    _tree_container: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
        <style id="tree-style">
            :host { display: block; min-width: max-content; box-sizing: border-box;  }
            .tree-node-header { margin: 0; user-select: none; white-space: nowrap; overflow: hidden;      
                    display: flex; align-items: center; padding: 2px; font-size: 12px; 
                    min-width: max-content; border-radius: 4px; }
            .tree-node-header.selected { background-color: rgba(31, 111, 235, 0.3) !important; }
            .tree-node-chevron { width: 16px; height: 16px; }
            .tree-node-text { display: inline-flex; padding: 2px 4px; align-items: center }
            .tree-node-children { overflow: auto; min-width: max-content;}
        </style>
        <div data-name="_tree_container"></div>
        """
        self.old_root = None
        self.selectedNode = None

    @cached_property
    def root(self) -> NodeList:
        node = UiNode()
        node.set_surrogate_root()
        self._tree_container.append(node.dom_node)
        return node


# Demo component that showcases the CustomTreeUI usage
class CustomTreeDemo(wpc.Component, tag_name='custom-tree-demo'):
    fileTree: CustomTreeUI = wpc.element()
    orgTree: CustomTreeUI = wpc.element()
    div1: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        self.element.shadowRoot.innerHTML = """
<style>
    :host { display: block; }
    .tree-container { background: #161b22; border-radius: 8px; padding: 0px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3); border: 1px solid #30363d; margin-bottom: 30px; }
    .demo-title { color: #f0f6fc; margin-bottom: 10px; font-size: 1.2em; }
</style>

<div data-name="div1"></div>
        """

    async def after_init_component(self):
        # JSON for file system tree
        svg_icon_1 = SvgIcon.from_file(AllIcons.toolWindowComponents_dark)
        def click(ev):
            logger.debug('clicked')
            ev.stopPropagation()
            ev.preventDefault()
        svg_icon_1.element.addEventListener('click', create_proxy(click))
        svg_icon_1.border = '2px solid #3574F0'
        # svg_icon_1.host_style.set('border-left', '5px solid transparent')
        # svg_icon_1.host_style.set('border', None)
        svg_icon_1.host_style['border-left'] = '5px solid transparent'
        svg_icon_1.host_style['border'] = ''
        file_system_json = {
            'text': '📁 Project Root',
            'children': [
                {'text': '📁 source', 'expanded': True,
                 'additional': svg_icon_1, 'children': [
                    {'text': '📁 components', 'expanded': True, 'children': [
                        {'text': '📄 Button.js 1234567890 1234567890 1234567890'},
                        {'text': '📄 Modal.js', 'selected': True},
                        {'text': '📄 Tree.js', 'backgroundColor': '#3d2817'}
                    ]},
                    {'text': '📁 utils', 'expanded': True, 'backgroundColor': '#2d4a22', 'children': [
                        {'text': '📄 helpers.py'},
                        {'text': '📄 validators.py'}
                    ]}
                ]},
                {'text': '📁 tests', 'children': [
                    {'text': '📄 test_tree.py'},
                    {'text': '📄 many children.py', 'children': []}
                ]}
            ]
        }
        # programmatically add n=50 additional nodes to 'tests' folder
        tests_folder = file_system_json['children'][1]['children'][1]['children']
        for i in range(50):
            tests_folder.append({
                'text': f'📄 test_file_{i}.py',
                'backgroundColor': '#2d4a22' if i % 2 == 0 else '#3d2817'
            })
        # JSON for organization tree
        org_json = {
            'text': '🏢 Company',
            'children': [
                {'text': '👷 Engineering', 'children': [
                    {'text': '👨‍💻 Backend Team'},
                    {'text': '👩‍💻 Frontend Team'}
                ]},
                {'text': '🧑‍💼 HR'}
            ]
        }
        self.create_tree(file_system_json, "height: 200px; overflow: auto")
        self.create_tree(org_json)

    def create_tree(self, json_node: dict, style: str = ''):
        div = js.document.createElement('div')
        div.className = 'tree-container'
        if style:
            div.setAttribute('style', style)
        tree = CustomTreeUI()
        div.append( tree.element )
        self.create_tree_from_json(json_node, tree.root)
        self.div1.append(div)

    def create_tree_from_json(self, json_node: dict, parent: NodeList):
        children_data = json_node.get('children', [])
        for child in children_data:
            node = UiNode()
            node.text = child.get('text', 'Unnamed')
            node.backgroundColor = child.get('backgroundColor', '')
            node.expanded = child.get('expanded', False)
            node.selected = child.get('selected', False)
            additional = child.get('additional', None)
            if additional:
                node.additional(additional)
            parent.children.append(node)

            self.create_tree_from_json(child, node)

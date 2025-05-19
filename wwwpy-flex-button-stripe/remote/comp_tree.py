from __future__ import annotations
import inspect

import logging
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import js
import wwwpy.remote.component as wpc
import wwwpy.remote.designer.ui.new_toolbox  # noqa
from wwwpy.common.designer.comp_info import iter_comp_info_folder, CompInfo
from wwwpy.common.designer.element_library import ElementDef, ElementDefBase
from wwwpy.common.designer.html_parser import CstTree
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.ui.design_aware import DesignAware
from wwwpy.remote.designer.ui.intent import IntentEvent, Intent
from wwwpy.remote.designer.ui.intent_add_element import AddElementIntent
from wwwpy.remote.designer.ui.new_toolbox import NewToolbox
from wwwpy.remote.designer.ui.svg_icon import SvgIcon

logger = logging.getLogger(__name__)


class _DesignAware(DesignAware):

    def find_intent(self, hover_event: IntentEvent):
        target = hover_event.deep_target
        res = target.closest(CompTreeItem.component_metadata.tag_name)
        if res:
            comp_tree_item: CompTreeItem = wpc.get_component(res)

            return comp_tree_item.add_intent
        return None


_design_aware = _DesignAware()


class CompTree(wpc.Component, tag_name='wwwpy-comp-tree'):
    _div: js.HTMLDivElement = wpc.element()

    def init_component(self):
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
<style>
    
    details > details {
        margin-left: 1em;
    }
    
    .no-marker > summary {
      list-style: none;
      padding-left: 0.5em;
    }
    .no-marker > summary::-webkit-details-marker {
      display: none;
    }
</style>

<div data-name="_div">component-tree</div>
        """

        for ci in iter_comp_info_folder(Path(__file__).parent, 'remote'):
            cti = CompTreeItem()
            cti.set_comp_info(ci)
            self._div.appendChild(cti.element)

    def connectedCallback(self):
        DesignAware.EP_REGISTRY.unregister(_design_aware)
        DesignAware.EP_REGISTRY.register(_design_aware)

    def disconnectedCallback(self):
        DesignAware.EP_REGISTRY.unregister(_design_aware)


class CompTreeItem(wpc.Component, tag_name='wwwpy-comp-tree-item'):
    comp_info: CompInfo
    _details: js.HTMLElement = wpc.element()
    _summary: js.HTMLElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<details data-name="_details" open>
    <summary data-name="_summary"></summary>
</details>
        """

    def set_comp_info(self, ci: CompInfo):
        self.comp_info = ci
        self._summary.innerText = ci.class_name

        def rec(cst_tree: CstTree, elem: js.HTMLElement):
            for cst_node in cst_tree:
                summary = cst_node.tag_name
                dn = cst_node.attributes.get('data-name', None)
                if dn:
                    summary += f' / {dn}'

                # language=html
                html = f"""
<details open>
  <summary>{summary}</summary>              
</details>                
"""

                logger.debug(f'html=`{html}`')
                ch = js.document.createRange().createContextualFragment(html)

                elem.appendChild(ch)
                last_ch = elem.lastElementChild
                if len(cst_node.children) == 0:
                    last_ch.classList.add('no-marker')
                else:
                    rec(cst_node.children, last_ch)

        try:
            rec(ci.cst_tree, self._details)
        except:
            logger.exception('Error in CompTreeItem.set_comp_info')
            self._details.innerText = 'Error in CompTreeItem.set_comp_info'

    @cached_property
    def add_intent(self) -> Intent:
        tag_name = self.comp_info.tag_name
        label = f'Add {tag_name}'
        intent = AddElementIntent(label)
        python_type = self.comp_info.class_name
        element_def_min: ElementDefBase = ElementDefBase(tag_name, python_type)
        intent.element_def = element_def_min
        return intent

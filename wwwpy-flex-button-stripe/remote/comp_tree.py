from __future__ import annotations

import logging
from pathlib import Path

import js
import wwwpy.remote.component as wpc
import wwwpy.remote.designer.ui.new_toolbox  # noqa
from wwwpy.common.designer.comp_info import iter_comp_info_folder, CompInfo
from wwwpy.common.designer.html_parser import CstTree
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer.ui.new_toolbox import NewToolbox
from wwwpy.remote.designer.ui.svg_icon import SvgIcon

logger = logging.getLogger(__name__)


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

        for ci in iter_comp_info_folder(Path(__file__).parent):
            cti = CompTreeItem()
            cti.set_comp_info(ci)
            self._div.appendChild(cti.element)


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
                dn = cst_node.attributes.get('data-name',None)
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

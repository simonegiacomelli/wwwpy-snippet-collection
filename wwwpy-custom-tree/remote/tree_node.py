from __future__ import annotations

import logging
from abc import ABC
from functools import cached_property

from wwwpy.common.collectionlib import ObservableList

logger = logging.getLogger(__name__)

_node_id = 0


class NodeList(ABC):

    @property
    def children(self) -> list[Node]: ...

    @property
    def parent(self) -> NodeList | None: ...

    def selected_nodes(self) -> set[Node]: ...

    def deselect_all(self, recursive: bool = True): ...

    def root(self) -> NodeList:
        if self.parent is None:
            return self
        return self.parent.root()


class Node(NodeList, ABC):
    selected: bool = False
    expanded: bool = False
    text: str = ''
    icon: str = ''
    backgroundColor: str = ''

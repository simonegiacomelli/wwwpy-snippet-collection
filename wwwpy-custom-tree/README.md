# Incubator for custom tree and new Component Structure implementation.

## TODO

- Add tests for the ui tree
- Decouple well the common part, i.e., tree_node.py vs custom_tree_ui.py
- Implement tree features needed by comp_structure.py:
  - scroll node into view
  - Event handling - e.g., on before expand to lazy load
  - Event handling - e.g., on click on a Location node to change the selection in the canvas
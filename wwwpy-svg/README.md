
# SVG icon development

The goal is to preprocess with python internal xml libs the xml and:


add_rect
- read the svg original width/height (e.g. 20x20), assert it's a square and the same as the viewBox width/height
- we have a ratio (1.4) so we calculate the new width/height (e.g. 28x28)
- we calculate the x/y offset (20-28)/2 = -4
- we set the svg attr: viewBox="-4 -4 28 28", width="28" height="28"
- we add a rect with the same size as the svg, x=-4, y=-4

import xml.etree.ElementTree as ET
from typing import Callable, Dict

AttributeMutator = Callable[[Dict[str, str]], None]


def build_document(svg: str, attribute_mutator: AttributeMutator) -> str:
    root = ET.fromstring(svg)
    for elem in root.iter():
        attribute_mutator(elem.attrib)
    return ET.tostring(root, encoding='unicode')


from typing import Dict, Callable
import xml.etree.ElementTree as ET

def add_rounded_background(svg: str, fill_color: str, radius: float) -> str:
    root = ET.fromstring(svg)
    x, y, w, h = root.attrib.get('viewBox', '0 0 0 0').split()
    ns = '{http://www.w3.org/2000/svg}'
    bg = ET.Element(ns + 'rect', {
        'x': x,
        'y': y,
        'width': w,
        'height': h,
        'fill': fill_color,
        'rx': str(radius),
        'ry': str(radius)
    })
    root.insert(0, bg)
    for e in root.iter():
        if isinstance(e.tag, str) and e.tag.startswith('{'):
            e.tag = e.tag.split('}', 1)[1]
    for k in list(root.attrib):
        if k.startswith('xmlns'):
            root.attrib.pop(k)
    root.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
    return ET.tostring(root, encoding='unicode')

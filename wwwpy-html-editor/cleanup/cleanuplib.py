from pathlib import Path

import bs4
from bs4 import BeautifulSoup  # requires beautifulsoup4
from lxml import etree, html
import logging

logger = logging.getLogger(__name__)

# attacch console handler to see debug messages
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def run_example_cleanup():
    content = Path(__file__).with_name('file.html').read_text()
    logger.debug(f'Content len={len(content)}')
    clean_content = cleanup(content)
    Path(__file__).with_name('file-cleaned.html').write_text(clean_content)
    print(clean_content)


def cleanup(content: str, remove_vals: dict | None = None) -> str:
    """
    Cleanup HTML content by removing specified CSS properties.
    remove_vals: dict mapping CSS property names to values to remove.
    """
    # default properties and their values to remove
    # font-family: Arial, Helvetica, sans-serif; font-size: small
    default_remove = {
        'color': 'rgb(211, 207, 201)',
        'background-color': 'rgb(24, 26, 27)',
        'font-family': 'Arial, Helvetica, sans-serif',
        'font-size': 'small',
    }
    remove_vals = remove_vals or default_remove
    # parse HTML and remove specific style properties
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(style=True):
        styles = [d.strip() for d in tag['style'].split(';') if d.strip()]
        new_styles = []
        for decl in styles:
            if ':' not in decl:
                continue
            prop, val = [p.strip() for p in decl.split(':', 1)]
            # skip removal values
            if prop in remove_vals and val == remove_vals[prop]:
                continue
            new_styles.append(f"{prop}: {val}")
        if new_styles:
            tag['style'] = '; '.join(new_styles)
        else:
            del tag['style']
    uff = str(soup)
    uff = uff.replace(u'\xa0', u' ')
    uff = bs4.BeautifulSoup(uff, preserve_whitespace_tags=["p"])
    # document_root = html.fromstring(uff)
    # uff = etree.tostring(document_root, encoding='unicode', pretty_print=True)
    return str(uff)


if __name__ == '__main__':
    run_example_cleanup()
    print('Example cleanup script executed.')

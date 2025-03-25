from js import document

from remote.simple_dark_theme import simple_dark_theme_header


async def main():
    document.head.insertAdjacentHTML('beforeend', simple_dark_theme_header)
    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'

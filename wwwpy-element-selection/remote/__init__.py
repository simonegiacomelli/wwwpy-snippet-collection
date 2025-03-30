from js import document

from remote.simple_dark_theme import simple_dark_theme_header


async def main():
    document.head.insertAdjacentHTML('beforeend', simple_dark_theme_header)

    from . import element_selector  # register ElementSelector component
    from . import main_component    # register MainComponent

    # Set up the main component as the root element
    document.body.innerHTML = '<main-component></main-component>'
from js import document


async def main():
    from . import element_selector  # register ElementSelector component
    from . import main_component    # register MainComponent

    # Set up the main component as the root element
    document.body.innerHTML = '<main-component></main-component>'
from js import document

async def main():
    from . import accordion_components  # Register accordion components
    from . import accordion_demo  # Register accordion demo component
    document.body.innerHTML = '<accordion-demo></accordion-demo>'
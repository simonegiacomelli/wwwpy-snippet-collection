from js import document
from wwwpy.remote import simple_dark_theme


async def main():
    # from wwwpy.remote import shoelace
    # shoelace.setup_shoelace()
    simple_dark_theme.setup()
    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'

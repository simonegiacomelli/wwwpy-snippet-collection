from js import document

from remote.simple_dark_theme import set_simple_dark_theme


async def main():
    set_simple_dark_theme()
    from . import log_levels
    log_levels.setup()
    from . import component1  # for component registration
    from . import sidebar_demo
    from . import pushable_sidebar
    # document.body.innerHTML = '<component-1></component-1>'
    document.body.innerHTML = '<sidebar-demo></sidebar-demo>'

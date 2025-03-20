from js import document
from wwwpy.remote.jslib import script_load_once


async def main():
    from wwwpy.remote import shoelace
    shoelace.setup_shoelace()

    await script_load_once('https://d3js.org/d3.v7.min.js')

    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'

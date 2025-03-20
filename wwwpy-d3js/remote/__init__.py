from js import document
from wwwpy.common.asynclib import create_task_safe
from wwwpy.remote import micropip_install
from wwwpy.remote.jslib import script_load_once


async def main():
    from wwwpy.remote import shoelace
    shoelace.setup_shoelace()

    d3task =  create_task_safe(script_load_once('https://d3js.org/d3.v7.min.js'))

    document.body.innerHTML = 'Installing pip libraries<br>'
    for lib in ['pydantic']:
        document.body.insertAdjacentHTML('beforeend', f'<div>Installing {lib}...</div>')
        await micropip_install(lib)

    await d3task

    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'

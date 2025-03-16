from js import document
import js

from wwwpy.server.rpc4tests import rpctst_exec


async def test1():
    document.body.innerHTML = '<input id="input1" type="text">'

    inp : js.HTMLInputElement = document.getElementById('input1')
    inp.focus()

    await rpctst_exec("page.locator('#input1').press_sequentially('yellow1')")

    assert inp.value == 'yellow1'

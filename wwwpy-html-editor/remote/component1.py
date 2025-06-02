import asyncio
import inspect
import logging
from dataclasses import dataclass
from pathlib import Path

from pyodide.ffi import create_proxy
import js
import wwwpy.remote.component as wpc
from wwwpy.common import state
from wwwpy.remote import dict_to_js

from server import rpc

logger = logging.getLogger(__name__)

@dataclass
class AppState:
    content: str = ''
    filename: str = ''

class Component1(wpc.Component, tag_name='component-1'):
    _btn_copy_html: js.HTMLButtonElement = wpc.element()
    _btn_save: js.HTMLButtonElement = wpc.element()
    _filename: js.HTMLInputElement = wpc.element()
    _editor: js.HTMLElement = wpc.element()
    _html_output: js.HTMLElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
 
<style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #121212;
            color: #e0e0e0;
        }

        .container {
            background: #1e1e1e;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        #toolbar {
            background: #2e2e2e;
            padding: 10px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }

        #toolbar button {
            padding: 6px 12px;
            border: 1px solid #555;
            background: #3a3a3a;
            color: #e0e0e0;
            cursor: pointer;
            border-radius: 4px;
            font-size: 14px;
            transition: all 0.2s;
        }

        #toolbar button:hover {
            background: #4a4a4a;
            border-color: #777;
        }

        #toolbar button:active {
            background: #5a5a5a;
        }

        .separator {
            width: 1px;
            background: #444;
            margin: 0 4px;
        }

        #editor {
            min-height: 300px;
            padding: 20px;
            outline: none;
            font-size: 16px;
            line-height: 1.6;
            background: #1e1e1e;
            color: #e0e0e0;
        }

        #editor:focus {
            background: #2a2a2a;
        }

        #htmlOutput {
            background: #121212;
            color: #cfcfcf;
            font-family: 'Consolas', 'Monaco', monospace;
            padding: 20px;
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 14px;
            min-height: 100px;
            max-height: 300px;
            overflow-y: auto;
        }

        .output-header {
            background: #2e2e2e;
            padding: 10px 20px;
            border-top: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .output-header h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: #495057;
        }

        .copy-btn {
            padding: 4px 12px;
            background: #0062cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        .copy-btn:hover {
            background: #0056b3;
        }

        .success-background {
            background-color: #28a745;
        }
        
        .failure-background {
            background-color: #dc3545;
        }

        table {
            border-collapse: collapse;
            margin: 10px 0;
        }

        td, th {
            border: 1px solid #555;
            padding: 8px;
            min-width: 50px;
        }

        th {
            background: #2e2e2e;
        }

        a {
            color: #4ea1d3;
            text-decoration: underline;
        }

        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }
    </style>
    
    <div class="container">
        <div id="toolbar">
            <button data-cmd="undo" title="Undo">↶</button>
            <button data-cmd="redo" title="Redo">↷</button>
            <div class="separator"></div>
            <button data-cmd="bold" title="Bold"><b>B</b></button>
            <button data-cmd="italic" title="Italic"><i>I</i></button>
            <button data-cmd="underline" title="Underline"><u>U</u></button>
            <button data-cmd="strikeThrough" title="Strikethrough"><s>S</s></button>
            <div class="separator"></div>
            <button data-cmd="formatBlock" data-value="h1" title="Heading 1">H1</button>
            <button data-cmd="formatBlock" data-value="h2" title="Heading 2">H2</button>
            <button data-cmd="formatBlock" data-value="h3" title="Heading 3">H3</button>
            <button data-cmd="formatBlock" data-value="p" title="Paragraph">¶</button>
            <div class="separator"></div>
            <button data-cmd="insertUnorderedList" title="Bullet List">• List</button>
            <button data-cmd="insertOrderedList" title="Numbered List">1. List</button>
            <div class="separator"></div>
            <button data-cmd="justifyLeft" title="Align Left">⬅</button>
            <button data-cmd="justifyCenter" title="Align Center">⬌</button>
            <button data-cmd="justifyRight" title="Align Right">➡</button>
            <div class="separator"></div>
            <button data-cmd="createLink" title="Insert Link">🔗 Link</button>
            <button data-cmd="insertImage" title="Insert Image">🖼 Image</button>
            <button data-cmd="insertTable" title="Insert Table">⊞ Table</button>
            <div class="separator"></div>
            <button data-cmd="removeFormat" title="Clear Formatting">✕ Clear</button>
            
<input data-name="_filename" placeholder="e.g., filename.html"><button data-name="_btn_save">Save</button>
        </div>

        <div id="editor" data-name='_editor' contenteditable="true"></div>

        <div class="output-header">
            <h3>HTML Output (Live Preview)</h3>
            <button class="copy-btn" data-name="_btn_copy_html">Copy HTML</button>
        </div>

        <pre id="htmlOutput" data-name="_html_output"></pre>
    </div>
"""
        self._state = state._restore(AppState)
        self._filename.value = self._state.filename
        self._editor.innerHTML = self._state.content


    async def after_init_component(self):
        self.editor = self.element.querySelector('#editor')
        self.htmlOutput = self.element.querySelector('#htmlOutput')
        self.toolbar = self.element.querySelector('#toolbar')

        def updateHTMLOutput(e=None):
            self.htmlOutput.textContent = self.editor.innerHTML
            self._state.content = self.editor.innerHTML

        update_proxy = create_proxy(updateHTMLOutput)
        self.editor.addEventListener('input', update_proxy)
        self.editor.addEventListener('DOMNodeInserted', update_proxy)
        self.editor.addEventListener('DOMNodeRemoved', update_proxy)
        for btn in self.toolbar.querySelectorAll('button'):
            def handler(evt, btn=btn):
                if not hasattr(btn.dataset, 'cmd'):
                    return
                evt.preventDefault()
                cmd = btn.dataset.cmd
                val = btn.dataset.value or None
                if cmd == 'createLink':
                    url = js.prompt('Enter URL:')
                    if url:
                        js.document.execCommand(cmd, False, url)
                        updateHTMLOutput()
                        return
                if cmd == 'insertImage':
                    url = js.prompt('Enter image URL:')
                    if url:
                        js.document.execCommand(cmd, False, url)
                        updateHTMLOutput()
                        return
                if cmd == 'insertTable':
                    rows = int(js.prompt('Number of rows:') or 0)
                    cols = int(js.prompt('Number of columns:') or 0)
                    if rows and cols:
                        table = '<table><tbody>'
                        for i in range(rows):
                            table += '<tr>'
                            for j in range(cols):
                                table += '<td>&nbsp;</td>'
                            table += '</tr>'
                        table += '</tbody></table>'
                        js.document.execCommand('insertHTML', False, table)
                        updateHTMLOutput()
                        return
                js.document.execCommand(cmd, False, val)
                updateHTMLOutput()
                self.editor.focus()

            btn.addEventListener('click', create_proxy(handler))

    async def _btn_copy_html__click(self, event):
        html = self.editor.innerHTML
        js.navigator.clipboard.writeText(html)
        btn = event.target
        original = btn.textContent
        btn.textContent = '✓ Copied!'
        btn.classList.add('success-background')

        def reset():
            btn.textContent = original
            btn.classList.remove('success-background')

        js.setTimeout(create_proxy(reset), 2000)

    async def _btn_save__click(self, event):
        original = self._btn_save.textContent
        self._btn_save.textContent = 'Saving...'
        try:
            await self._do_save()
            self._btn_save.textContent = 'Saved!'
            _state_success(self._btn_save)
        except Exception as e:
            logger.exception('Error saving file', exc_info=e)
            _state_failure(self._btn_save)
            self._btn_save.textContent = 'Save failed'
            js.alert(f'Error saving file: {e}')
        await asyncio.sleep(2)
        self._btn_save.textContent = original
        _state_clear(self._btn_save)

    async def _do_save(self):
        html = self.editor.innerHTML
        html_bytes = bytes(html, 'utf-8')
        filename_strip = self._filename.value.strip()
        if filename_strip:
            filename = str(Path(filename_strip).with_suffix('.html'))
        else:
            filename = 'index.html'

        if await rpc.file_exists(filename):
            if not js.window.confirm(f'File `{filename}` already exists. Overwrite?'):
                logger.info(f'User cancelled overwrite for {filename}')
                return
        await rpc.file_save(filename, html_bytes)
        return # disabled image saving for now
        img_count = 0
        # query all img tags under _editor
        imgs = self.editor.querySelectorAll('img')
        for img in imgs:
            src = img.getAttribute('src')
            if not src:
                continue
            img_count += 1
            img_filename = f'image_{img_count}.png'
            if src.startswith('data:image/'):
                # Extract base64 data
                base64_data = src.split(',')[1]
                # Decode base64 data WITH PYTHON NOT js.atob!
                import base64
                byte_array = base64.b64decode(base64_data)
                await rpc.file_save(img_filename, byte_array)
            else:  # Assume it's a URL and fetch it
                logger.debug(f'Fetching image from `{src}`')
                # response = await js.window.fetch(src, dict_to_js({
                #     'credentials': 'include',
                #     'mode': 'cors',
                #     'cache': 'force-cache'
                # }))
                response = await _fetch(src)
                if response.ok:
                    blob = await response.blob()
                    array_buffer = await blob.arrayBuffer()
                    byte_array = js.Uint8Array.new(array_buffer)
                    # Save the image file
                    await rpc.file_save(img_filename, byte_array)
                else:
                    logger.error(f'Failed to fetch image from {src}: {response.status} {response.statusText}')
    
    async def _filename__input(self, event):
        logger.debug(f'{inspect.currentframe().f_code.co_name} event fired %s', event)
        self._state.filename = self._filename.value
    


def _state_success(button: js.HTMLButtonElement):
    button.style.backgroundColor = 'green'


def _state_failure(button: js.HTMLButtonElement):
    button.style.backgroundColor = 'red'


def _state_clear(button: js.HTMLButtonElement):
    button.style.backgroundColor = ''


async def _fetch(url: str) -> js.Response:
    return await js.window.fetch(url, dict_to_js({
        # "headers": {
        #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        #     "priority": "u=0, i",
        #     "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        #     "sec-ch-ua-arch": "\"x86\"",
        #     "sec-ch-ua-bitness": "\"64\"",
        #     "sec-ch-ua-form-factors": "\"Desktop\"",
        #     "sec-ch-ua-full-version": "\"136.0.7103.113\"",
        #     "sec-ch-ua-full-version-list": "\"Chromium\";v=\"136.0.7103.113\", \"Google Chrome\";v=\"136.0.7103.113\", \"Not.A/Brand\";v=\"99.0.0.0\"",
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-model": "\"\"",
        #     "sec-ch-ua-platform": "\"Linux\"",
        #     "sec-ch-ua-platform-version": "\"6.11.0\"",
        #     "sec-ch-ua-wow64": "?0",
        #     "sec-fetch-dest": "document",
        #     "sec-fetch-mode": "navigate",
        #     "sec-fetch-site": "none",
        #     "sec-fetch-user": "?1",
        #     "upgrade-insecure-requests": "1",
        #     "x-browser-channel": "stable",
        #     "x-browser-copyright": "Copyright 2025 Google LLC. All rights reserved.",
        #     "x-browser-validation": "ctYldj7UqvsGWB62N+qJrQZxvXA=",
        #     "x-browser-year": "2025",
        #     "x-client-data": "CK21yQEIlLbJAQijtskBCKmdygEI84vLAQiUocsBCJGjywEIh6DNAQj+pc4BCK/tzgEI3e7OAQiQ8c4BCK7xzgEIkfLOAQ=="
        # },
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": None,
        "method": "GET",
        "mode": "cors",
        "credentials": "include"
    }))

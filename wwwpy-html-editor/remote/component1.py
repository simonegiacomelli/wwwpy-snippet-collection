import logging

import js
import wwwpy.remote.component as wpc

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):

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

        .copy-btn.copied {
            background: #28a745;
        }

        /* Table styles */
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

        /* Link styles */
        a {
            color: #4ea1d3;
            text-decoration: underline;
        }

        /* List styles */
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
    </div>

    <div id="editor" contenteditable="true">

    </div>

    <div class="output-header">
        <h3>HTML Output (Live Preview)</h3>
        <button class="copy-btn" onclick="copyHTML()">Copy HTML</button>
    </div>

    <pre id="htmlOutput"></pre>
</div>
"""

    

from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from wwwpy.remote import dict_to_js
from pyodide.ffi import create_proxy

from .accordion_components import AccordionContainer


class AccordionDemo(wpc.Component, tag_name='accordion-demo'):
    # Define elements we'll interact with
    accordion: AccordionContainer = wpc.element()
    event_log: js.HTMLElement = wpc.element()

    # Define buttons
    toggle_section1_btn: js.HTMLElement = wpc.element()
    toggle_section2_btn: js.HTMLElement = wpc.element()
    toggle_section3_btn: js.HTMLElement = wpc.element()
    expand_all_btn: js.HTMLElement = wpc.element()
    collapse_all_btn: js.HTMLElement = wpc.element()
    add_section_btn: js.HTMLElement = wpc.element()

    def init_component(self):
        """Initialize the accordion demo component."""
        self.element.attachShadow(dict_to_js({'mode': 'open'}))
        # language=html
        self.element.shadowRoot.innerHTML = """
        <style>
            :host {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.5;
            }

            .demo-container {
                margin: 30px 0;
            }

            accordion-container {
                display: block;
                border: 1px solid #ddd;
                border-radius: 4px;
                overflow: hidden;
            }

            .controls {
                margin: 15px 0;
            }

            button {
                margin: 5px;
                padding: 8px 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }

            button:hover {
                background-color: #0069d9;
            }

            #event-log {
                margin-top: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>

        <h1>Improved Accordion with Shadow DOM</h1>
        <p>This demo shows the accordion components using Shadow DOM for better encapsulation and cleaner implementation.</p>

        <div class="controls">
            <h3>Controls</h3>
            <button data-name="toggle_section1_btn">Toggle Section 1</button>
            <button data-name="toggle_section2_btn">Toggle Section 2</button>
            <button data-name="toggle_section3_btn">Toggle Section 3</button>
            <button data-name="expand_all_btn">Expand All</button>
            <button data-name="collapse_all_btn">Collapse All</button>
            <button data-name="add_section_btn">Add new section</button>
        </div>

        <div class="demo-container">
            <wwwpy-accordion-container data-name="accordion" >
                <wwwpy-accordion-section>
                    <div slot="header">Section 1: Introduction</div>
                    <div slot="panel">
                        <p>Try clicking on this header or using the control buttons below.</p>
                    </div>
                </wwwpy-accordion-section>

                <wwwpy-accordion-section>
                    <div slot="header">Section 2: Content</div>
                    <div slot="panel">
                        <p>Lorem ipsum:</p>
                        <ul>
                            <li>Lorem ipsum dolor sit amet, consectetur adipiscing elit</li>
                            <li>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</li>
                            <li>Ut enim ad minim veniam, quis nostrud exercitation ullamco</li>
                            <li>Duis aute irure dolor in reprehenderit in voluptate velit esse</li>
                        </ul>
                    </div>
                </wwwpy-accordion-section>

                <wwwpy-accordion-section>
                    <div slot="header">Section 3: More Content</div>
                    <div slot="panel">
                        <p>Additional content:</p>
                        <ul>
                            <li>Cillum dolore eu fugiat nulla pariatur</li>
                            <li>Excepteur sint occaecat cupidatat non proident</li>
                            <li>Sunt in culpa qui officia deserunt mollit anim id est laborum</li>
                            <li>Et harum quidem rerum facilis est et expedita distinctio</li>
                        </ul>
                    </div>
                </wwwpy-accordion-section>
            </wwwpy-accordion-container>

            <div id="event-log" data-name="event_log">
                <p>Event log will appear here when sections are toggled.</p>
            </div>
        </div>
        """

    def connectedCallback(self):
        """Called when the element is inserted into the DOM."""

    def _log(self, message):
        """Add a message to the event log."""
        # Remove the first child if there are more than 5 entries
        if self.event_log.children.length > 5:
            self.event_log.removeChild(self.event_log.firstChild)

        # Create and append a new log entry
        log_entry = js.document.createElement('p')
        log_entry.innerHTML = message
        self.event_log.appendChild(log_entry)

    def _toggle_section(self, index):
        """Toggle a specific accordion section."""
        sections = self.accordion.sections
        if index < len(sections):
            section = sections[index]
            section.toggle()
            self._log(
                f"<strong>Programmatic:</strong> Section {index + 1} was toggled (now {'expanded' if section.expanded else 'collapsed'})")

    def accordion__accordion_toggle(self, event):
        self._log(f'<strong>Event:</strong> Section toggled by user click')
        section = event.detail.section
        sections = self.accordion.sections
        try:
            section_index = sections.index(section)
            status = 'expanded' if section.expanded else 'collapsed'
            self._log(f"<strong>Event:</strong> Section index {section_index} was {status} by user click")
        except ValueError:
            self._log(f"<strong>Event:</strong> Section not found in the accordion")

    async def toggle_section1_btn__click(self, event):
        """Handle toggle section 1 button click."""
        self._toggle_section(0)

    async def toggle_section2_btn__click(self, event):
        """Handle toggle section 2 button click."""
        self._toggle_section(1)

    async def toggle_section3_btn__click(self, event):
        """Handle toggle section 3 button click."""
        self._toggle_section(2)

    async def expand_all_btn__click(self, event):
        """Handle expand all button click."""
        self.accordion.expand_all()
        self._log("<strong>Programmatic:</strong> All sections expanded")

    async def collapse_all_btn__click(self, event):
        """Handle collapse all button click."""
        self.accordion.collapse_all()
        self._log("<strong>Programmatic:</strong> All sections collapsed")

    async def add_section_btn__click(self, event):
        count = len(self.accordion.sections) + 1
        # language=html
        html = f"""
<wwwpy-accordion-section>
<div slot="header">Section {count}: Dynamic Content</div>
<div slot="panel">
<p>Dynamically added section {count}:</p>
<ul>
<li>This section was added programmatically</li>
<li>The accordion container detects new sections automatically</li>
<li>Each section manages its own expanded state</li>
<li>Shadow DOM provides better encapsulation</li>
</ul>
</div>
</wwwpy-accordion-section>"""
        frag = js.document.createRange().createContextualFragment(html)
        self.accordion.element.appendChild(frag)

        self._log(f"<strong>Programmatic:</strong> New section {count} added")

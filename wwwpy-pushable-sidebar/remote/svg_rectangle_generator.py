from __future__ import annotations

import wwwpy.remote.component as wpc
import js
from wwwpy.remote import dict_to_js
import logging

logger = logging.getLogger(__name__)


class SvgRectangleGenerator(wpc.Component, tag_name='svg-rectangle-generator'):
    # Input elements
    width_input: js.HTMLInputElement = wpc.element()
    height_input: js.HTMLInputElement = wpc.element()
    x_input: js.HTMLInputElement = wpc.element()
    y_input: js.HTMLInputElement = wpc.element()
    glow_option: js.HTMLSelectElement = wpc.element()

    # Display elements
    svg_container: js.HTMLDivElement = wpc.element()
    svg_code: js.HTMLPreElement = wpc.element()

    def init_component(self):
        """Initialize the component."""
        self.element.attachShadow(dict_to_js({'mode': 'open'}))

        # HTML template with CSS styles
        # language=html
        self.element.shadowRoot.innerHTML = """
<style>
    :host {
        display: block;
        font-family: Arial, sans-serif;
        margin: 20px;
    }
    .container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 30px;
        margin-bottom: 20px;
    }
    .controls {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .svg-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    label {
        display: inline-block;
        width: 120px;
        margin-bottom: 10px;
    }
    input {
        width: 60px;
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 10px;
    }
    button:hover {
        background-color: #45a049;
    }
    .code-display {
        margin-top: 20px;
        width: 90%;
        max-width: 800px;
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        overflow-x: auto;
    }
    pre {
        margin: 0;
        white-space: pre-wrap;
    }

    /* CSS Animations for pulsing effect */
    @keyframes pulse {
        0% { stroke-width: 2; opacity: 1; }
        50% { stroke-width: 5; opacity: 0.7; }
        100% { stroke-width: 2; opacity: 1; }
    }

    .pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
</style>

<h1>Interactive SVG Rectangle Generator</h1>

<div class="container">
    <div class="controls">
        <h2>Parameters</h2>
        <div>
            <label for="width_input">w (width):</label>
            <input type="number" data-name="width_input" value="200" min="10" max="500" step="10">
        </div>
        <div>
            <label for="height_input">h (height):</label>
            <input type="number" data-name="height_input" value="150" min="10" max="500" step="10">
        </div>
        <div>
            <label for="x_input">x (horizontal inset):</label>
            <input type="number" data-name="x_input" value="40" min="1" max="100" step="5">
        </div>
        <div>
            <label for="y_input">y (vertical inset):</label>
            <input type="number" data-name="y_input" value="30" min="1" max="100" step="5">
        </div>
        <div>
            <label for="glow_option">Pulse Effect:</label>
            <select data-name="glow_option">
                <option value="none">No Effect</option>
                <option value="top_left">Top & Left</option>
                <option value="bottom_right">Bottom & Right</option>
                <option value="inner">Inner Rectangle</option>
            </select>
        </div>
    </div>

    <div class="svg-container" data-name="svg_container">
        <!-- SVG will be inserted here -->
    </div>
</div>

<div class="code-display">
    <h3>SVG Code:</h3>
    <pre data-name="svg_code"></pre>
</div>
"""

    async def after_init_component(self):
        """Called after initialization. Generate SVG on startup."""
        self.generate_svg()

    def generate_svg(self):
        """Generate SVG based on current input values."""
        # Get parameter values from inputs
        w = float(self.width_input.value)
        h = float(self.height_input.value)
        x = float(self.x_input.value)
        y = float(self.y_input.value)
        glow_option = self.glow_option.value

        # Generate SVG
        svg_string = create_svg(w, h, x, y, glow_option)

        # Update the display
        self.svg_container.innerHTML = svg_string
        self.svg_code.textContent = svg_string

    # Event handlers
    async def width_input__input(self, event):
        """Handle width input changes."""
        self.generate_svg()

    async def height_input__input(self, event):
        """Handle height input changes."""
        self.generate_svg()

    async def x_input__input(self, event):
        """Handle x input changes."""
        self.generate_svg()

    async def y_input__input(self, event):
        """Handle y input changes."""
        self.generate_svg()

    async def glow_option__change(self, event):
        """Handle glow option changes."""
        self.generate_svg()


def create_svg(w, h, x, y, pulse_option) -> str:
    """Create SVG string based on parameters."""
    # Validate to ensure inner rectangle has positive dimensions
    if x * 2 >= w or y * 2 >= h:
        return f'<text x="10" y="30" fill="red">Error: Inset values too large for the given width/height</text>'

    # Calculate inner rectangle dimensions
    inner_width = w - 2 * x
    inner_height = h - 2 * y

    # Determine which parts should pulse
    top_class, left_class, bottom_class, right_class, inner_class = [''] * 5

    pulse = 'class="pulse" stroke="cyan"'
    if pulse_option == "top_left":
        top_class = pulse
        left_class = pulse
    elif pulse_option == "bottom_right":
        bottom_class = pulse
        right_class = pulse
    elif pulse_option == "inner":
        inner_class = pulse

    # Create SVG string with the CSS classes for animation
    return f'''<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
            <!-- Outer rectangle segments -->
            <line x1="0" y1="0" x2="{w}" y2="0" stroke="blue" stroke-width="2" {top_class} />
            <line x1="0" y1="0" x2="0" y2="{h}" stroke="blue" stroke-width="2" {left_class} />
            <line x1="0" y1="{h}" x2="{w}" y2="{h}" stroke="blue" stroke-width="2" {bottom_class} />
            <line x1="{w}" y1="0" x2="{w}" y2="{h}" stroke="blue" stroke-width="2" {right_class} />

            <!-- Inner rectangle -->
            <rect x="{x}" y="{y}" width="{inner_width}" height="{inner_height}" fill="none" stroke="red" stroke-width="2" {inner_class} />

            <!-- Line connecting bottom-left corners -->
            <line x1="0" y1="{h}" x2="{x}" y2="{h - y}" stroke="green" stroke-width="2" />

            <!-- Line connecting top-right corners -->
            <line x1="{w}" y1="0" x2="{w - x}" y2="{y}" stroke="purple" stroke-width="2" />
        </svg>'''

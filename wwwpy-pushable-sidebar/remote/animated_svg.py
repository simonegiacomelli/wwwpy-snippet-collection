# language=html
animated_svg_html = """
<svg style='width: 200px ; height: 200px;' viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g>
        <!-- Main diagonal line (arrow body) - shorter -->
        <line x1="70" y1="70" x2="0" y2="0" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>

        <!-- First arrowhead segment -->
        <line x1="-3" y1="0" x2="47" y2="0" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>

        <!-- Second arrowhead segment -->
        <line x1="0" y1="-3" x2="0" y2="47" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>
        <animateTransform
                attributeName="transform"
                type="translate"
                values="3,3; 10,10; 3,3"
                dur="1s"
                repeatCount="indefinite"
                additive="sum"/>
    </g>
</svg>

<svg  style='width: 200px ; height: 200px;' viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g>
        <!-- Main diagonal line (arrow body) - shorter -->
        <line x1="30" y1="30" x2="100" y2="100" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>

        <!-- First arrowhead segment (horizontal) -->
        <line x1="53" y1="100" x2="103" y2="100" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>

        <!-- Second arrowhead segment (vertical) -->
        <line x1="100" y1="53" x2="100" y2="103" stroke-width="6" stroke="black">
            <animate
                    attributeName="stroke"
                    values="black;white;black"
                    dur="1.5s"
                    repeatCount="indefinite"/>
        </line>
        <animateTransform
                attributeName="transform"
                type="translate"
                values="-3,-3; -10,-10; -3,-3"
                dur="1s"
                repeatCount="indefinite"
                additive="sum"/>
    </g>
</svg>
"""

/**
 * PushableSidebar - A vanilla JS library for creating sidebars that push content
 *
 * Features:
 * - Left or right positioning
 * - Resizable via drag handle
 * - Collapsible with animation
 * - Shadow DOM for style isolation
 * - Compatible with arbitrary web pages
 */

// Define the custom element only once
class PushableSidebar extends HTMLElement {
    constructor() {
        super();

        // Attach Shadow DOM for style isolation
        this.attachShadow({ mode: 'open' });

        // States: 'hidden', 'collapsed', 'expanded'
        this._state = 'expanded';

        // Default configuration
        this._config = {
            position: 'left',        // 'left' or 'right'
            width: '300px',          // Initial width when expanded
            minWidth: '50px',        // Minimum width when resizing
            maxWidth: '500px',       // Maximum width when resizing
            collapsedWidth: '30px',  // Width when collapsed
            zIndex: 9999             // z-index for the sidebar
        };

        // Resize state
        this._isResizing = false;
        this._startWidth = 0;
        this._startX = 0;
        this._ticking = false;     // For requestAnimationFrame

        // Bind methods to this
        this._handleResize = this._handleResize.bind(this);
        this._stopResize = this._stopResize.bind(this);
        this.toggle = this.toggle.bind(this);
    }

    // Define observed attributes for configuration
    static get observedAttributes() {
        return [
            'position', 'width', 'min-width', 'max-width',
            'collapsed-width', 'z-index', 'state'
        ];
    }

    // Handle attribute changes
    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue === newValue) return;

        switch(name) {
            case 'position':
                this._config.position = newValue;
                break;
            case 'width':
                this._config.width = newValue;
                break;
            case 'min-width':
                this._config.minWidth = newValue;
                break;
            case 'max-width':
                this._config.maxWidth = newValue;
                break;
            case 'collapsed-width':
                this._config.collapsedWidth = newValue;
                break;
            case 'z-index':
                this._config.zIndex = newValue;
                break;
            case 'state':
                if (['hidden', 'collapsed', 'expanded'].includes(newValue)) {
                    this._state = newValue;
                } else {
                    console.warn('Invalid state. Valid values are: hidden, collapsed, expanded');
                }
                break;
        }

        // Update the sidebar if it's already connected
        if (this.isConnected) {
            this._updateSidebar();
        }
    }

    // When element is added to the DOM
    connectedCallback() {
        // Set up the sidebar structure and styles
        this._render();

        // Apply initial state
        this._updateSidebar();

        // Add resize event listener for responsive behavior
        window.addEventListener('resize', () => {
            this._adjustContentPadding();
        });
    }

    // When element is removed from the DOM
    disconnectedCallback() {
        // Remove the padding from body when sidebar is removed
        this._removePadding();

        // Clean up event listeners
        window.removeEventListener('resize', this._adjustContentPadding);

        // Remove all event listeners for drag resize
        if (this._resizeHandle) {
            this._resizeHandle.removeEventListener('mousedown', this._startResize);
            document.removeEventListener('mousemove', this._handleResize);
            document.removeEventListener('mouseup', this._stopResize);
            document.removeEventListener('mouseleave', this._stopResize);
        }
    }

    // Create the HTML structure and CSS
    _render() {
        const position = this._config.position;
        const animationSpeed = 300; // Fixed animation speed

        // Define the styles
        const style = document.createElement('style');
        style.textContent = `
      :host {
        display: ${this._state === 'hidden' ? 'none' : 'block'};
        position: fixed;
        top: 0;
        ${position}: 0;
        height: 100%;
        box-sizing: border-box;
        z-index: ${this._config.zIndex};
        transition: width ${animationSpeed}ms ease;
        width: ${this._state === 'collapsed' ? this._config.collapsedWidth : this._config.width};
        overflow: hidden;
      }
      
      .sidebar-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        background-color: #333;
        color: #fff;
        box-shadow: ${position === 'left' ? '2px' : '-2px'} 0 5px rgba(0, 0, 0, 0.1);
        box-sizing: border-box;
        transition: transform ${animationSpeed}ms ease;
      }
      
      .sidebar-header {
        display: flex;
        justify-content: ${position === 'left' ? 'flex-end' : 'flex-start'};
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #444;
      }
      
      .sidebar-header-buttons {
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      
      .toggle-button, .close-button {
        background: none;
        border: none;
        cursor: pointer;
        color: #fff;
        font-size: 16px;
        padding: 8px 5px;
        margin: 5px 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
      }
      
      .toggle-button:hover, .close-button:hover {
        background-color: rgba(255, 255, 255, 0.1);
      }
      
      .close-button {
        font-size: 18px;
      }
      
      .sidebar-content {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
      }
      
      .resize-handle {
        position: absolute;
        top: 0;
        ${position === 'left' ? 'right' : 'left'}: 0;
        width: 8px; /* Wider handle for easier grabbing */
        height: 100%;
        cursor: ${position === 'left' ? 'e-resize' : 'w-resize'};
        background-color: transparent;
        transition: background-color 0.2s;
        z-index: 2; /* Ensure it's above content */
        touch-action: none; /* Better touch handling */
      }
      
      .resize-handle:hover,
      .resize-handle.active {
        background-color: rgba(255, 255, 255, 0.2);
      }
      
      /* When collapsed, only show the toggle button */
      :host([state="collapsed"]) .sidebar-content,
      :host([state="collapsed"]) .resize-handle {
        opacity: 0;
      }
      
      :host([state="collapsed"]) .sidebar-header {
        border-bottom: none;
      }
    `;

        // Create the sidebar structure
        const container = document.createElement('div');
        container.className = 'sidebar-container';

        // Create the header with toggle and close buttons
        const header = document.createElement('div');
        header.className = 'sidebar-header';

        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'sidebar-header-buttons';

        const toggleButton = document.createElement('button');
        toggleButton.className = 'toggle-button';
        toggleButton.title = this._state === 'collapsed' ? 'Expand sidebar' : 'Collapse sidebar';
        toggleButton.innerHTML = position === 'left'
            ? (this._state === 'collapsed' ? '&#9658;' : '&#9668;')  // Right or Left arrow
            : (this._state === 'collapsed' ? '&#9668;' : '&#9658;'); // Left or Right arrow
        toggleButton.addEventListener('click', this.toggle);

        const closeButton = document.createElement('button');
        closeButton.className = 'close-button';
        closeButton.title = 'Hide sidebar';
        closeButton.innerHTML = '&times;'; // × symbol
        closeButton.addEventListener('click', () => this.setState('hidden'));

        buttonContainer.appendChild(toggleButton);
        buttonContainer.appendChild(closeButton);
        header.appendChild(buttonContainer);

        // Create content area for slotted content
        const content = document.createElement('div');
        content.className = 'sidebar-content';
        const slot = document.createElement('slot');
        content.appendChild(slot);

        // Create resize handle
        const resizeHandle = document.createElement('div');
        resizeHandle.className = 'resize-handle';
        this._resizeHandle = resizeHandle;

        // Add resize event listeners
        resizeHandle.addEventListener('mousedown', (e) => {
            this._startResize(e);
        });

        // Assemble the sidebar
        container.appendChild(header);
        container.appendChild(content);
        container.appendChild(resizeHandle);

        // Add elements to shadow DOM
        this.shadowRoot.appendChild(style);
        this.shadowRoot.appendChild(container);

        // Save references
        this._toggleButton = toggleButton;
        this._closeButton = closeButton;
        this._container = container;
    }

    // Update sidebar appearance and behavior based on configuration
    _updateSidebar() {
        // Set attribute to match internal state
        this.setAttribute('state', this._state);

        // Handle display based on state
        if (this._state === 'hidden') {
            this.style.display = 'none';
            this._removePadding();
            return;
        } else {
            this.style.display = 'block';
        }

        // Update the width based on state
        this.style.width = this._state === 'collapsed'
            ? this._config.collapsedWidth
            : this._config.width;

        // Update toggle button icon and title
        if (this._toggleButton) {
            this._toggleButton.innerHTML = this._config.position === 'left'
                ? (this._state === 'collapsed' ? '&#9658;' : '&#9668;')
                : (this._state === 'collapsed' ? '&#9668;' : '&#9658;');

            this._toggleButton.title = this._state === 'collapsed' ? 'Expand sidebar' : 'Collapse sidebar';
        }

        // Update document body padding to make space for the sidebar
        this._adjustContentPadding();
    }

    // Adjust body padding to accommodate the sidebar
    _adjustContentPadding() {
        // Remove existing padding first
        this._removePadding();

        // Skip adding padding if sidebar is hidden
        if (this._state === 'hidden') return;

        // Add padding based on current sidebar state
        const currentWidth = this._state === 'collapsed'
            ? this._config.collapsedWidth
            : this.style.width || this._config.width;

        // Calculate padding with the px suffix if needed
        const paddingValue = currentWidth.endsWith('px')
            ? currentWidth
            : `${currentWidth}px`;

        // Apply padding to body to push content
        if (this._config.position === 'left') {
            document.body.style.paddingLeft = paddingValue;
        } else {
            document.body.style.paddingRight = paddingValue;
        }

        // Dispatch event for external components to react
        this.dispatchEvent(new CustomEvent('sidebar-resize', {
            detail: { width: currentWidth }
        }));
    }

    // Remove body padding
    _removePadding() {
        if (this._config.position === 'left') {
            document.body.style.paddingLeft = '';
        } else {
            document.body.style.paddingRight = '';
        }
    }

    // Start resize operation
    _startResize(e) {
        // If sidebar is in collapsed state, expand it first but keep the current width
        if (this._state === 'collapsed') {
            const currentWidth = this.style.width;
            this.setState('expanded');
            this.style.width = currentWidth; // Prevent jumping to stored width
        }

        this._isResizing = true;
        this._startWidth = parseInt(getComputedStyle(this).width, 10);
        this._startX = e.clientX;

        // Add active class to handle
        this._resizeHandle.classList.add('active');

        // Add event listeners for drag
        document.addEventListener('mousemove', this._handleResize, { passive: true });
        document.addEventListener('mouseup', this._stopResize);
        document.addEventListener('mouseleave', this._stopResize);

        // Prevent text selection during resize
        document.body.style.userSelect = 'none';

        // Add a resize class to the body to optimize rendering
        document.body.classList.add('sidebar-resizing');

        e.preventDefault();
    }

    // Handle resize during mouse move
    _handleResize(e) {
        if (!this._isResizing) return;

        // Use requestAnimationFrame to optimize performance
        if (!this._ticking) {
            this._ticking = true;

            requestAnimationFrame(() => {
                let newWidth;

                if (this._config.position === 'left') {
                    newWidth = this._startWidth + (e.clientX - this._startX);
                } else {
                    newWidth = this._startWidth - (e.clientX - this._startX);
                }

                // Apply min/max constraints
                const minWidth = parseInt(this._config.minWidth, 10);
                const maxWidth = parseInt(this._config.maxWidth, 10);

                if (newWidth < minWidth) newWidth = minWidth;
                if (newWidth > maxWidth) newWidth = maxWidth;

                // Update the sidebar width - directly set style for better performance
                this.style.width = `${newWidth}px`;

                // Update body padding directly for better performance
                if (this._config.position === 'left') {
                    document.body.style.paddingLeft = `${newWidth}px`;
                } else {
                    document.body.style.paddingRight = `${newWidth}px`;
                }

                this._ticking = false;
            });
        }
    }

    // End resize operation
    _stopResize() {
        if (!this._isResizing) return;

        this._isResizing = false;
        this._resizeHandle.classList.remove('active');

        // Remove event listeners
        document.removeEventListener('mousemove', this._handleResize);
        document.removeEventListener('mouseup', this._stopResize);
        document.removeEventListener('mouseleave', this._stopResize);

        // Restore text selection
        document.body.style.userSelect = '';

        // Remove resize class
        document.body.classList.remove('sidebar-resizing');

        // Store the final width in the config
        this._config.width = `${parseInt(this.style.width, 10)}px`;

        // Save the current width to localStorage if desired
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('pushable-sidebar-width', this._config.width);
        }

        // Fire an event for the resize completion
        this.dispatchEvent(new CustomEvent('sidebar-resize-end', {
            detail: { width: this._config.width }
        }));
    }

    // Public API methods

    // Set sidebar state ('hidden', 'collapsed', 'expanded')
    setState(state) {
        if (!['hidden', 'collapsed', 'expanded'].includes(state)) {
            console.warn('Invalid state. Valid states are: hidden, collapsed, expanded');
            return this;
        }

        const oldState = this._state;
        this._state = state;
        this._updateSidebar();

        // Dispatch event
        this.dispatchEvent(new CustomEvent('sidebar-state-change', {
            detail: {
                oldState: oldState,
                newState: state
            }
        }));

        return this;
    }

    // Get current state
    getState() {
        return this._state;
    }

    // Toggle sidebar state: expanded <-> collapsed, but hidden -> expanded
    toggle() {
        switch (this._state) {
            case 'hidden':
                this.setState('expanded');
                break;
            case 'expanded':
                this.setState('collapsed');
                break;
            case 'collapsed':
                this.setState('expanded');
                break;
        }
        return this;
    }

    // Set sidebar width programmatically
    setWidth(width) {
        this._config.width = width;
        if (this._state === 'expanded') {
            this.style.width = width;
            this._adjustContentPadding();
        }
        return this;
    }

    // Set sidebar position
    setPosition(position) {
        if (position !== 'left' && position !== 'right') {
            console.warn('Sidebar position must be "left" or "right"');
            return this;
        }

        // Remove current positioning
        this._removePadding();

        // Update position
        this._config.position = position;
        this.setAttribute('position', position);

        // Re-render the sidebar
        while (this.shadowRoot.firstChild) {
            this.shadowRoot.removeChild(this.shadowRoot.firstChild);
        }
        this._render();
        this._updateSidebar();

        return this;
    }
}

// Register the custom element
customElements.define('pushable-sidebar', PushableSidebar);

// Log registration success
console.log('PushableSidebar custom element registered successfully');
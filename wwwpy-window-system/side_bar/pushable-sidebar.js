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

class PushableSidebar extends HTMLElement {
    constructor() {
        super();

        // Attach Shadow DOM for style isolation
        this.attachShadow({ mode: 'open' });

        // Default configuration
        this._config = {
            position: 'left',        // 'left' or 'right'
            width: '300px',          // Initial width
            minWidth: '50px',        // Minimum width when resizing
            maxWidth: '500px',       // Maximum width when resizing
            collapsed: false,        // Initial state
            collapsedWidth: '30px',  // Width when collapsed
            zIndex: 9999,            // z-index for the sidebar
            theme: 'light',          // 'light' or 'dark'
            animationSpeed: 300      // Transition duration in ms
        };

        // State
        this._isResizing = false;
        this._startWidth = 0;
        this._startX = 0;

        // Bind methods to this
        this._handleResize = this._handleResize.bind(this);
        this._stopResize = this._stopResize.bind(this);
        this.toggle = this.toggle.bind(this);
    }

    // Define observed attributes for configuration
    static get observedAttributes() {
        return [
            'position', 'width', 'min-width', 'max-width',
            'collapsed', 'collapsed-width', 'z-index', 'theme'
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
            case 'collapsed':
                this._config.collapsed = newValue === 'true';
                break;
            case 'collapsed-width':
                this._config.collapsedWidth = newValue;
                break;
            case 'z-index':
                this._config.zIndex = newValue;
                break;
            case 'theme':
                this._config.theme = newValue;
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
        const theme = this._config.theme;

        // Define the styles
        const style = document.createElement('style');
        style.textContent = `
      :host {
        display: block;
        position: fixed;
        top: 0;
        ${position}: 0;
        height: 100%;
        box-sizing: border-box;
        z-index: ${this._config.zIndex};
        transition: width ${this._config.animationSpeed}ms ease;
        width: ${this._config.collapsed ? this._config.collapsedWidth : this._config.width};
        overflow: hidden;
      }
      
      .sidebar-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        background-color: ${theme === 'dark' ? '#333' : '#f5f5f5'};
        color: ${theme === 'dark' ? '#fff' : '#333'};
        box-shadow: ${position === 'left' ? '2px' : '-2px'} 0 5px rgba(0, 0, 0, 0.1);
        box-sizing: border-box;
        transition: transform ${this._config.animationSpeed}ms ease;
      }
      
      .sidebar-header {
        display: flex;
        justify-content: ${position === 'left' ? 'flex-end' : 'flex-start'};
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid ${theme === 'dark' ? '#444' : '#ddd'};
      }
      
      .toggle-button {
        background: none;
        border: none;
        cursor: pointer;
        color: ${theme === 'dark' ? '#fff' : '#333'};
        font-size: 16px;
        padding: 5px;
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
        width: 5px;
        height: 100%;
        cursor: ${position === 'left' ? 'e-resize' : 'w-resize'};
        background-color: transparent;
        transition: background-color 0.2s;
      }
      
      .resize-handle:hover,
      .resize-handle.active {
        background-color: rgba(0, 0, 0, 0.1);
      }
      
      /* When collapsed, only show the toggle button */
      :host([collapsed="true"]) .sidebar-content,
      :host([collapsed="true"]) .resize-handle {
        opacity: 0;
      }
      
      :host([collapsed="true"]) .sidebar-header {
        border-bottom: none;
      }
    `;

        // Create the sidebar structure
        const container = document.createElement('div');
        container.className = 'sidebar-container';

        // Create the header with toggle button
        const header = document.createElement('div');
        header.className = 'sidebar-header';

        const toggleButton = document.createElement('button');
        toggleButton.className = 'toggle-button';
        toggleButton.innerHTML = position === 'left'
            ? (this._config.collapsed ? '&#9658;' : '&#9668;')  // Right or Left arrow
            : (this._config.collapsed ? '&#9668;' : '&#9658;'); // Left or Right arrow
        toggleButton.addEventListener('click', this.toggle);
        header.appendChild(toggleButton);

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
        this._container = container;
    }

    // Update sidebar appearance and behavior based on configuration
    _updateSidebar() {
        // Update the width
        this.style.width = this._config.collapsed
            ? this._config.collapsedWidth
            : this._config.width;

        // Update toggle button icon
        if (this._toggleButton) {
            this._toggleButton.innerHTML = this._config.position === 'left'
                ? (this._config.collapsed ? '&#9658;' : '&#9668;')
                : (this._config.collapsed ? '&#9668;' : '&#9658;');
        }

        // Set collapsed attribute for CSS styling
        if (this._config.collapsed) {
            this.setAttribute('collapsed', 'true');
        } else {
            this.setAttribute('collapsed', 'false');
        }

        // Update document body padding to make space for the sidebar
        this._adjustContentPadding();
    }

    // Adjust body padding to accommodate the sidebar
    _adjustContentPadding() {
        // Remove existing padding first
        this._removePadding();

        // Add padding based on current sidebar state
        const currentWidth = this._config.collapsed
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
        if (this._config.collapsed) return;

        this._isResizing = true;
        this._startWidth = parseInt(getComputedStyle(this).width, 10);
        this._startX = e.clientX;

        // Add active class to handle
        this._resizeHandle.classList.add('active');

        // Add event listeners for drag
        document.addEventListener('mousemove', this._handleResize);
        document.addEventListener('mouseup', this._stopResize);
        document.addEventListener('mouseleave', this._stopResize);

        // Prevent text selection during resize
        document.body.style.userSelect = 'none';

        e.preventDefault();
    }

    // Handle resize during mouse move
    _handleResize(e) {
        if (!this._isResizing) return;

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

        // Update the sidebar width
        this.style.width = `${newWidth}px`;
        this._config.width = `${newWidth}px`;

        // Update body padding to match
        this._adjustContentPadding();

        e.preventDefault();
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

        // Save the current width to localStorage if desired
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('pushable-sidebar-width', this._config.width);
        }
    }

    // Public API methods

    // Toggle sidebar collapsed state
    toggle() {
        this._config.collapsed = !this._config.collapsed;
        this._updateSidebar();

        // Dispatch event
        this.dispatchEvent(new CustomEvent('sidebar-toggle', {
            detail: { collapsed: this._config.collapsed }
        }));

        return this._config.collapsed;
    }

    // Set sidebar width programmatically
    setWidth(width) {
        this._config.width = width;
        if (!this._config.collapsed) {
            this.style.width = width;
            this._adjustContentPadding();
        }
        return this;
    }

    // Collapse the sidebar
    collapse() {
        if (!this._config.collapsed) {
            this.toggle();
        }
        return this;
    }

    // Expand the sidebar
    expand() {
        if (this._config.collapsed) {
            this.toggle();
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

    // Set theme
    setTheme(theme) {
        this._config.theme = theme;
        this.setAttribute('theme', theme);
        return this;
    }
}

// Register the custom element
customElements.define('pushable-sidebar', PushableSidebar);

// Register the custom element
customElements.define('pushable-sidebar', PushableSidebar);

// Log registration success
console.log('PushableSidebar custom element registered successfully');
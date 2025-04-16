from js import document


async def main():
    from . import popup_notification  # For component registration
    # language=html
    document.body.innerHTML = '''
    <h1>Popup Notification Custom Element</h1>
    <p>A lightweight, customizable notification system implemented as a Web Component.</p>
    
    <h2>Demo</h2>
    <popup-demo></popup-demo>
    
    <h2>Usage</h2>
    <p>Use JavaScript to show notifications:</p>
    <pre>
    // Get reference to the custom element
    const popupEl = document.querySelector('popup-notification');
    
    // Show a simple notification
    popupEl.show('This is a basic notification');
    
    // Show a typed notification
    popupEl.info('This is an info notification');
    popupEl.warning('This is a warning notification');
    popupEl.error('This is an error notification');
    popupEl.success('This is a success notification');
    </pre>
    '''
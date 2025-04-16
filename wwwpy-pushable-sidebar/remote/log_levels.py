import logging

def setup():
    # wwwpy.remote.designer.ui.palette
    # set the logger above to debug level
    # names = ['wwwpy.remote.designer.ui.palette']
    names = ['wwwpy.remote.designer.ui.drag_manager']
    for logger_name in names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
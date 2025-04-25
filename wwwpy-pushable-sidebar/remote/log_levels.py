import logging


def setup():
    # wwwpy.remote.designer.ui.palette
    # set the logger above to debug level
    # names = ['wwwpy.remote.designer.ui.palette']
    # names = ['wwwpy.remote.designer.ui.drag_manager']
    names = [
        # 'wwwpy.remote.designer.ui.toolbox',
        # 'wwwpy.remote.designer.ui.palette',
        # 'wwwpy.common.designer.element_path',
        # 'wwwpy.common.designer.code_strings',
        # 'wwwpy.common.designer.html_locator',
        # 'wwwpy.remote.designer.ui.drag_manager'
    ]
    for logger_name in names:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

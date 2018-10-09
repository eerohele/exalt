import os
import sublime

import Exalt.constants as constants
import Exalt.settings as settings
import Exalt.exalt as exalt


def set_status(view, message):
    view.set_status(constants.PLUGIN_NAME, message)


def get_content(view):
    return view.substr(sublime.Region(0, view.size()))


def reset_status(view):
    sublime.set_timeout(lambda:
                        view.erase_status(constants.PLUGIN_NAME),
                        constants.RESET_STATUS_TIMEOUT)


def get_syntax(view):
    syntax_file = view.settings().get("syntax")
    return os.path.splitext(os.path.basename(syntax_file))[0]


def has_xml_scope(scope):
    if not scope:
        return False
    else:
        scope_names = scope.split(" ")
        return any(map(lambda s: s.startswith("text.xml"), scope_names))


def is_xml(view):
    regions = view.sel()

    if not regions:
        return False
    else:
        position = regions[0].begin()
        scope = view.scope_name(position)
        return has_xml_scope(scope)


def is_html(view):
    return get_syntax(view) == "HTML"


def is_eligible(view):
    return is_xml(view) or is_html(view)


def is_xslt(view):
    return get_syntax(view) in ["XSL", "XSLT"]


def get_error_region(view, point):
    """Get the line the error's on."""
    line = view.line(point)
    return sublime.Region(line.begin(), line.end())


def get_error_point(view, error):
    """Get the error text point.

    lxml uses 1-based line and column numbers but ST wants them
    0-based, so subtract 1 from both."""
    return view.text_point(error.line - 1, error.column - 1)


def show_error(view, message, error=None):
    """Show the given error message in the Sublime Text status bar and
    highlight the error region if given."""
    set_status(view, str(message))

    if error is not None:
        point = get_error_point(view, error)
        region = get_error_region(view, point)

        exalt.error_point = point

        view.add_regions(constants.PLUGIN_NAME,
                         [region],
                         "variable.parameter",
                         "dot",
                         constants.SUBLIME_REGION_FLAGS)

        scroll = bool(exalt.get_settings()
                      .get(settings.AUTO_SCROLL_TO_ERROR, False))

        if scroll:
            view.show_at_center(point)

    return False

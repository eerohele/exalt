import io
import os
import sublime

import Markup.encodings as encodings
import Markup.constants as constants
import Markup.settings as settings
import Markup.markup as markup

def set_status(view, message):
    view.set_status(constants.PLUGIN_NAME, message)


def get_content(view):
    return view.substr(sublime.Region(0, view.size()))


def get_content_as_bytes(view):
    # I have no idea whether this is the optimal way of parsing the
    # content of the view. If you try to parse it as a string, you'll
    # get the error described here:
    #
    # http://lxml.de/parsing.html#python-unicode-strings
    #
    # There's an lxml bug report on the subject that seems to suggest that
    # using BytesIO is the way to go:
    #
    # https://bugs.launchpad.net/lxml/+bug/613302
    #
    # But I feel that the documentation and the bug report conflict each
    # other to some extent. Improvement suggestions appreciated.
    return io.BytesIO(bytes(get_content(view), encodings.UTF8))


def replace_region_content(view, edit, data):
    view.replace(edit, sublime.Region(0, view.size()), data)


def reset_status(view):
    sublime.set_timeout(lambda:
                        view.erase_status(constants.PLUGIN_NAME),
                        constants.RESET_STATUS_TIMEOUT)


def get_syntax(view):
    syntax_file = view.settings().get("syntax")
    return os.path.splitext(os.path.basename(syntax_file))[0]


def is_xml(view):
    return get_syntax(view) in ["XML", "XHTML", "XSL", "XSLT"]


def is_html(view):
    return get_syntax(view) == "HTML"


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


def show_error(view, message, error = None):
    """Show the given error message in the Sublime Text status bar and
    highlight the error region if given."""
    set_status(view, str(message))

    if error is not None:
        point = get_error_point(view, error)
        region = get_error_region(view, point)

        markup.error_point = point

        view.add_regions(constants.PLUGIN_NAME,
                              [region],
                              "variable.parameter",
                              "dot",
                              constants.SUBLIME_REGION_FLAGS)

        scroll = bool(markup.get_settings()
                      .get(settings.AUTO_SCROLL_TO_ERROR, False))

        if scroll:
            view.show_at_center(point)

    return False

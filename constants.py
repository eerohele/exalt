import sublime

PLUGIN_NAME = __name__.split(".")[0]

SUBLIME_REGION_FLAGS = sublime.PERSISTENT | \
    sublime.DRAW_EMPTY_AS_OVERWRITE | \
    sublime.DRAW_SOLID_UNDERLINE |    \
    sublime.DRAW_NO_FILL |            \
    sublime.DRAW_NO_OUTLINE

RESET_STATUS_TIMEOUT = 6500

LXML_NO_DTD_FOUND = "no DTD found"
XML_MODEL = "xml-model"
APPLICATION_XML = "application/xml"
VERSION = "version"

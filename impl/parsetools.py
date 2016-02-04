import Exalt.view as vu
import Exalt.messages as messages
import Exalt.exalt as exalt
import Exalt.utils as utils

from lxml import etree


def get_parser(view, **kwargs):
    if vu.is_xml(view):
        return etree.XMLParser(**kwargs)
    elif vu.is_html(view):
        return etree.HTMLParser(**kwargs)
    else:
        raise Exception(messages.NO_PARSER_FOR_SYNTAX % exalt.get_syntax(view))


def parse_string(view, parser, string):
    if vu.is_eligible(view):
        return etree.parse(utils.string_to_bytes(string), parser)
    else:
        raise Exception(messages.CANNOT_PARSE_EXCEPTION)

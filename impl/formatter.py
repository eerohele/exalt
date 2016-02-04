import Exalt.view as vu
import Exalt.messages as messages
import Exalt.encodings as encodings

from lxml import etree

import Exalt.impl.parsetools as parsetools


def format_xml(xml, xml_declaration=False):
    encoding = xml.docinfo.encoding

    return etree.tostring(
        xml,
        pretty_print=True,
        xml_declaration=xml_declaration,
        encoding=encoding
    ).decode(encoding)


def format_region(view, region, xml_declaration=False):
    if vu.is_eligible(view):
        try:
            parser = parsetools.get_parser(view,
                                           encoding=encodings.UTF8,
                                           remove_blank_text=True,
                                           recover=True)

            xml = parsetools.parse_string(view, parser, view.substr(region))
            return format_xml(xml, xml_declaration)
        except etree.XMLSyntaxError:
            vu.set_status(view, messages.NOT_WELL_FORMED_XML)
            vu.reset_status(view)

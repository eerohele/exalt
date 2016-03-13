import Exalt.view as vu
import Exalt.messages as messages
import Exalt.encodings as encodings

from lxml import etree

import Exalt.impl.parsetools as parsetools


def format_markup(markup, view, **kwargs):
    encoding = markup.docinfo.encoding

    # lxml only indents HTML if method == "xml", but then it will self-close
    # any <script> element, which is not OK.
    #
    # This hack adds a single space into any empty <script> elements, which
    # forces lxml to add the closing tag.
    if (vu.is_html(view)):
        for script in markup.xpath("//script[@src][not(normalize-space(.))]"):
            script.text = " "

    return etree.tostring(
        markup,
        pretty_print=True,
        encoding=encoding,
        **kwargs
    ).decode(encoding)


def format_region(view, region, **kwargs):
    if vu.is_eligible(view):
        try:
            parser = parsetools.get_parser(view,
                                           encoding=encodings.UTF8,
                                           remove_blank_text=True,
                                           recover=True)

            markup = parsetools.parse_string(view, parser, view.substr(region))
            return format_markup(markup, view, **kwargs)
        except etree.XMLSyntaxError:
            vu.set_status(view, messages.NOT_WELL_FORMED_XML)
            vu.reset_status(view)

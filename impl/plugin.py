"""This module implements a Sublime Text 3 plugin for formatting and validating
XML and HTML markup."""

import os
import sublime

from sublime_plugin import TextCommand, EventListener

import Exalt.messages as messages
import Exalt.encodings as encodings
import Exalt.constants as constants
import Exalt.exalt as exalt
import Exalt.view as View

# XML_CATALOG_FILES needs to be set *before* lxml is loaded:
# http://permalink.gmane.org/gmane.comp.python.lxml.devel/7501
os.environ["XML_CATALOG_FILES"] = exalt.get_catalog_files()

# lxml is delivered as a Package Control dependency.
#
# See https://packagecontrol.io/docs/dependencies.
from lxml import etree
from lxml import isoschematron

import Exalt.impl.validator as validator

invoke_async = sublime.set_timeout_async


class ExaltTextCommand(TextCommand):
    def get_parser(self, **kwargs):
        view = self.view

        if View.is_xml(view):
            return etree.XMLParser(**kwargs)
        elif View.is_html(view):
            return etree.HTMLParser(**kwargs)
        else:
            raise Exception(messages.NO_PARSER_FOR_SYNTAX %
                            exalt.get_syntax(view))

    def parse_view_content(self, parser):
        view = self.view

        if View.is_xml(view) or View.is_html(view):
            return etree.parse(View.get_content_as_bytes(view), parser)
        else:
            raise Exception(messages.CANNOT_PARSE_EXCEPTION)


class ExaltClearCacheCommand(ExaltTextCommand):
    def run(self, edit):
        exalt.parser_cache.clear()


class ExaltFormatCommand(ExaltTextCommand):
    def format(self, document):
        encoding = document.docinfo.encoding

        return etree.tostring(
            document,
            pretty_print = True,
            xml_declaration = View.is_xml(self.view),
            encoding = encoding
        ).decode(encoding)

    def run(self, edit):
        view = self.view

        if View.is_xml(view) or View.is_html(view):
            try:
                # The "remove_blank_text" flag needs to be True for pretty-printing to
                # work. See http://stackoverflow.com/a/9612463/825783.
                #
                # TODO: Make "recover" a Sublime setting.
                parser = self.get_parser(encoding = encodings.UTF8,
                                         remove_blank_text = True,
                                         recover = True)

                content = self.parse_view_content(parser)
                View.replace_region_content(view, edit, self.format(content))
            except etree.XMLSyntaxError:
                View.set_status(view, messages.NOT_WELL_FORMED_XML)
                View.reset_status(view)


class ExaltValidateCommand(ExaltTextCommand):
    def run(self, edit):
        view = self.view

        if not View.is_xml(view) or len(View.get_content(view).strip()) == 0:
            return

        try:
            parser = self.get_parser(encoding = encodings.UTF8)
            document = self.parse_view_content(parser)

            if View.is_xslt(view):
                version = document.getroot().get(constants.VERSION)
                relax_ng = validator.get_xslt_relaxng_path(version)

                v = validator.get_validator_for_namespace( \
                      isoschematron.RELAXNG_NS)(view, document, relax_ng)

                invoke_async(lambda: v, 0)
            else:
                invoke_async(lambda: validator.try_validate(view, document), 0)
        except etree.XMLSyntaxError as e:
            message = str(e)

            if not constants.LXML_NO_DTD_FOUND in message:
                error = parser.error_log.filter_from_errors()[0]
                return View.show_error(view, message, error)


class ExaltGoToErrorCommand(TextCommand):
    def run(self, edit):
        self.view.show_at_center(exalt.error_point)


class ExaltValidate(EventListener):
    def on_pre_save_async(self, view):
        view.run_command("exalt_validate")

    def on_load_async(self, view):
        view.run_command("exalt_validate")

    def on_activated_async(self, view):
        view.run_command("exalt_validate")

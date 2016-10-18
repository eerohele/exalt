"""This module implements a Sublime Text 3 plugin for formatting and validating
XML and HTML markup."""

import os
import sublime
import sublime_api

from functools import partial
from sublime_plugin import TextCommand, EventListener

import Exalt.encodings as encodings
import Exalt.constants as constants
import Exalt.exalt as exalt
import Exalt.view as vu

# XML_CATALOG_FILES needs to be set *before* lxml is loaded:
# http://permalink.gmane.org/gmane.comp.python.lxml.devel/7501
os.environ["XML_CATALOG_FILES"] = exalt.get_catalog_files()

# lxml is delivered as a Package Control dependency.
#
# See https://packagecontrol.io/docs/dependencies.
from lxml import etree
from lxml import isoschematron

import Exalt.impl.parsetools as parsetools
import Exalt.impl.validator as validator
import Exalt.impl.formatter as formatter

invoke_async = sublime.set_timeout_async


class ExaltClearCacheCommand(TextCommand):
    def run(self, edit):
        exalt.parser_cache.clear()


class ExaltFormatCommand(TextCommand):
    def run(self, edit):
        view = self.view

        if (view.sel()[0].empty()):
            view.run_command("exalt_format_document")
        else:
            view.run_command("exalt_format_selections")


class ExaltCanonicalizeDocumentCommand(TextCommand):
    def run(self, edit):
        view = self.view
        region = sublime.Region(0, view.size())
        c14n = formatter.canonicalize_document(view, region)
        view.replace(edit, region, c14n)


class ExaltFormatDocumentCommand(ExaltFormatCommand):
    def run(self, edit):
        view = self.view
        region = sublime.Region(0, view.size())

        formatted = formatter.format_region(
            view,
            region,
            xml_declaration=vu.is_xml(view)
        )

        view.replace(edit, region, formatted)


class ExaltFormatSelectionsCommand(ExaltFormatCommand):
    SPACE = " "
    TAB = "\t"
    NEWLINE = "\n"

    # Indent the region with the same indentation level as the previous line.
    def guess_indentation_level(self, region):
        view = self.view
        (x, y) = view.rowcol(max(0, region.begin() - 1))
        prev_line_region = sublime.Region(view.text_point(x, y)).begin()
        return sublime_api.view_indentation_level(view.id(), prev_line_region)

    def indent_line(self, region, line):
        view = self.view
        tab_size = view.settings().get("tab_size")
        spaces = view.settings().get("translate_tabs_to_spaces")
        character = self.SPACE if spaces else self.TAB
        level = self.guess_indentation_level(region)
        return character * level * tab_size + line

    def indent(self, xml_string, region):
        lines = map(partial(self.indent_line, region), xml_string.splitlines())
        return self.NEWLINE.join(lines)

    def run(self, edit):
        view = self.view

        for region in view.sel():
            xml = self.indent(formatter.format_region(view, region), region)
            view.replace(edit, region, xml)


class ExaltValidateCommand(TextCommand):
    def run(self, edit):
        view = self.view

        if not vu.is_xml(view) or len(vu.get_content(view).strip()) == 0:
            return

        try:
            parser = parsetools.get_parser(view, encoding=encodings.UTF8)
            doc = parsetools.parse_string(view, parser, vu.get_content(view))

            if vu.is_xslt(view):
                version = doc.getroot().get(constants.VERSION)
                relax_ng = validator.get_xslt_relaxng_path(version)

                v = validator.get_validator_for_namespace(
                      isoschematron.RELAXNG_NS)(view, doc, relax_ng)

                invoke_async(lambda: v, 0)
            else:
                invoke_async(lambda: validator.try_validate(view, doc), 0)
        except etree.XMLSyntaxError as e:
            message = str(e)

            if constants.LXML_NO_DTD_FOUND not in message:
                error = parser.error_log.filter_from_errors()[0]
                return vu.show_error(view, message, error)


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

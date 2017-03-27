import sublime
import sys
import os

from unittest import TestCase
from urllib.request import pathname2url

exalt = sys.modules["Exalt.exalt"]

import Exalt.constants as constants
import Exalt.messages as messages
import Exalt.impl.plugin as plugin

# NOTE: These unit tests require that you've cloned the
# https://github.com/eerohele/catalogs repo (or an otherwise sufficient
# set of XML catalogs) and have set up Exalt to use those catalogs.


def read_file(path):
    return open(os.path.join(exalt.get_plugin_path(),
                             "tests/fixtures",
                             path), "r").read()


def expand_schema_location(document):
    schema = exalt.file_to_uri(os.path.join(exalt.get_plugin_path(),
                              "tests/fixtures/schemas"))

    return sublime.expand_variables(document, {"schema": schema})

# If we have these in a separate module, we need to restart ST3 every time
# after adding a new fixture, so we'll keep them here.
#
# Python 3.3 doesn't have enums, either.
VALID_INTERNAL_SUBSET = read_file("markup/valid_internal_subset.xml")
VALID_RNG = read_file("markup/valid_rng.xml")
VALID_RNG_NO_SCHEMATYPENS = read_file("markup/valid_rng_no_schematypens.xml")
VALID_DTD = expand_schema_location(read_file("markup/valid_dtd.xml"))
VALID_DTD_SYSTEM_URL = expand_schema_location(read_file("markup/valid_dtd_system_url.xml"))
VALID_SCHEMA_LOCATION = read_file("markup/valid_schema_location.xml")
VALID_ISO_SCHEMATRON = expand_schema_location(read_file("markup/valid_iso_schematron.xml"))
VALID_PRE_ISO_SCHEMATRON = expand_schema_location(read_file("markup/valid_pre_iso_schematron.xml"))
VALID_XHTML = read_file("markup/valid_xhtml.html")
VALID_XSLT = read_file("markup/valid.xsl")

INVALID_INTERNAL_SUBSET = read_file("markup/invalid_internal_subset.xml")
INVALID_RNG = read_file("markup/invalid_rng.xml")
INVALID_DTD = expand_schema_location(read_file("markup/invalid_dtd.xml"))
INVALID_DTD_SYSTEM_URL = expand_schema_location(read_file("markup/invalid_dtd_system_url.xml"))
INVALID_RNG_NO_SCHEMATYPENS = read_file("markup/invalid_rng_no_schematypens.xml")
INVALID_SCHEMA_LOCATION = read_file("markup/invalid_schema_location.xml")
INVALID_ISO_SCHEMATRON = expand_schema_location(read_file("markup/invalid_iso_schematron.xml"))
INVALID_PRE_ISO_SCHEMATRON = expand_schema_location(read_file("markup/invalid_pre_iso_schematron.xml"))
INVALID_XHTML = read_file("markup/invalid_xhtml.html")
INVALID_XSLT = read_file("markup/invalid.xsl")

NON_WELL_FORMED_XML = read_file("markup/non_well_formed.xml")


class TestExaltPlugin(TestCase):
    def test_file_to_uri(self):
        self.assertEqual(
            exalt.file_to_uri("/usr/local/bin/diff"),
            "file:///usr/local/bin/diff"
        )

        assert(
            "~" not in exalt.file_to_uri("~/.local")
        )


class ExaltTestCase(TestCase):
    def setUpClass():
        plugin.invoke_async = sublime.set_timeout

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.set_syntax_file("Packages/XML/XML.tmLanguage")

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.sel().clear()
            self.view.window().focus_view(self.view)
            self.view.window().run_command("close_file")

    def tearDownClass():
        plugin.invoke_async = sublime.set_timeout_async

    def set_html_syntax(self):
        self.view.set_syntax_file("Packages/HTML/HTML.tmLanguage")

    def set_xslt_syntax(self):
        syntax_file = "Packages/%s/XSLT.tmLanguage" % constants.PLUGIN_NAME
        self.view.set_syntax_file(syntax_file)

    def add_content_to_view(self, content):
        self.view.run_command("insert", {"characters": content})

    def get_view_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))


class TestExaltFormatCommand(ExaltTestCase):
    def run_command_and_compare(self, command, content, after):
        self.add_content_to_view(content)
        self.view.run_command(command)
        self.assertEqual(self.get_view_content(), after)

    def test_canonicalize_xml_document(self):
        content = """<a d="e" b="c"/>"""
        after = """<a b="c" d="e"></a>"""

        self.run_command_and_compare("exalt_canonicalize_document", content, after)

    def test_format_xml_document(self):
        content = """<pokemon><name>Pikachu</name><level>1</level></pokemon>"""
        after = """<?xml version='1.0' encoding='UTF-8'?>
<pokemon>
  <name>Pikachu</name>
  <level>1</level>
</pokemon>
"""
        self.run_command_and_compare("exalt_format", content, after)

    def test_format_html_document(self):
        self.set_html_syntax()
        content = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>title</title><link rel="stylesheet" href="style.css">
<script src="script.js"></script></head><body><p>Hello, world!</p></body>
</html>"""
        after = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <title>title</title>
    <link rel="stylesheet" href="style.css"/>
    <script src="script.js"> </script>
  </head>
  <body>
    <p>Hello, world!</p>
  </body>
</html>
"""
        self.run_command_and_compare("exalt_format", content, after)

    def test_format_selection(self):
        content = """<?xml version='1.0' encoding='UTF-8'?>
<pokemon>
  <name>Pikachu</name>
  <level>1</level>
  <abilities><ability name="Static"/>
<ability name="Lightning Rod"/>   </abilities>
</pokemon>
"""
        after = """<?xml version='1.0' encoding='UTF-8'?>
<pokemon>
  <name>Pikachu</name>
  <level>1</level>
  <abilities>
    <ability name="Static"/>
    <ability name="Lightning Rod"/>
  </abilities>
</pokemon>
"""
        self.view.sel().add(sublime.Region(93, 175))
        self.run_command_and_compare("exalt_format", content, after)

    def test_format_multiple_selections(self):
        content = """<pokemon>
  <name>Pikachu</name>
  <level>1</level>
<abilities><ability name="Static"/>
<ability name="Lightning Rod"/>   </abilities>
<details><genderRatio
male="50%" female="50%"/><catchRate>190</catchRate>

</details>
</pokemon>
"""
        after = """<?xml version='1.0' encoding='UTF-8'?>
<pokemon>
  <name>Pikachu</name>
  <level>1</level>
  <abilities>
    <ability name="Static"/>
    <ability name="Lightning Rod"/>
  </abilities>
  <details>
    <genderRatio male="50%" female="50%"/>
    <catchRate>190</catchRate>
  </details>
</pokemon>
"""
        self.view.sel().add(sublime.Region(52, 134))
        self.view.sel().add(sublime.Region(135, 220))
        self.run_command_and_compare("exalt_format", content, after)


class ValidateTestCase(ExaltTestCase):
    def validate_content_and_assert_status(self, content, status):
        self.add_content_to_view(content)
        self.view.run_command("exalt_validate")
        self.assertEqual(self.view.get_status(constants.PLUGIN_NAME), status)


class TestExaltValidateCommandValid(ValidateTestCase):
    def test_validate_xml_valid_xslt(self):
        self.set_xslt_syntax()
        self.validate_content_and_assert_status(VALID_XSLT,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_internal_subset(self):
        self.validate_content_and_assert_status(VALID_INTERNAL_SUBSET,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_rng(self):
        self.validate_content_and_assert_status(VALID_RNG,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_rng_no_schematypens(self):
        self.validate_content_and_assert_status(VALID_RNG_NO_SCHEMATYPENS,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_dtd(self):
        self.validate_content_and_assert_status(VALID_DTD,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_dtd_system_url(self):
        self.validate_content_and_assert_status(VALID_DTD_SYSTEM_URL,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_schema_location(self):
        self.validate_content_and_assert_status(VALID_SCHEMA_LOCATION,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_iso_schematron(self):
        self.validate_content_and_assert_status(VALID_ISO_SCHEMATRON,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_pre_iso_schematron(self):
        self.validate_content_and_assert_status(VALID_PRE_ISO_SCHEMATRON,
                                                messages.VALID_MARKUP)

    def test_validate_xml_valid_xhtml(self):
        self.validate_content_and_assert_status(VALID_XHTML,
                                                messages.VALID_MARKUP)


class TestExaltValidateCommandInvalid(ValidateTestCase):
    def test_validate_xml_invalid_xslt(self):
        self.set_xslt_syntax()
        self.validate_content_and_assert_status(INVALID_XSLT,
                                                "Invalid attribute INVALID for element template, line 5")

    def test_validate_xml_invalid_internal_subset(self):
        self.validate_content_and_assert_status(INVALID_INTERNAL_SUBSET,
                                                "Element person content does not follow the DTD, expecting (name , birthdate? , gender? , socialsecuritynumber?), got (name age birthdate gender ), line 11")

    def test_validate_xml_invalid_rng(self):
        self.validate_content_and_assert_status(INVALID_RNG,
                                                "Did not expect element INVALID there, line 7")

    def test_validate_xml_invalid_dtd(self):
        self.validate_content_and_assert_status(INVALID_DTD,
                                                "No declaration for element world, line 5")

    def test_validate_xml_invalid_dtd_system_url(self):
        self.validate_content_and_assert_status(INVALID_DTD_SYSTEM_URL,
                                                "No declaration for element INVALID, line 2")

    def test_validate_xml_invalid_rng_no_schematypens(self):
        self.validate_content_and_assert_status(INVALID_RNG_NO_SCHEMATYPENS,
                                                "Did not expect element INVALID there, line 6")

    def test_validate_xml_invalid_schema_location(self):
        self.validate_content_and_assert_status(INVALID_SCHEMA_LOCATION,
                                                "Element '{http://maven.apache.org/POM/4.0.0}INVALID': This element is not expected., line 7")

    def test_validate_xml_invalid_iso_schematron(self):
        self.validate_content_and_assert_status(INVALID_ISO_SCHEMATRON,
                                                "This section has no paragraphs")

    def test_validate_xml_invalid_pre_iso_schematron(self):
        self.validate_content_and_assert_status(INVALID_PRE_ISO_SCHEMATRON,
                                                "/ex:Person line 5: The element Person must have a Title attribute, line 5")

    def test_validate_xml_invalid_xhtml(self):
        self.validate_content_and_assert_status(INVALID_XHTML,
                                                "Element INVALID is not declared in p list of possible children, line 10")

    def test_validate_xml_non_well_formed(self):
        self.validate_content_and_assert_status(NON_WELL_FORMED_XML,
                                                "error parsing attribute name, line 11, column 5")

import os
import io

import Exalt.view as vu
import Exalt.messages as messages
import Exalt.encodings as encodings
import Exalt.constants as constants
import Exalt.namespaces as namespaces
import Exalt.utils as utils
import Exalt.exalt as exalt

from functools import partial

from lxml import etree
from lxml import isoschematron


##########
# PUBLIC #
##########


def get_xslt_relaxng_path(version):
    """Get XSLT RelaxNG schema path for version.

    Example:

       get_xslt_relaxng_path(2.0) => rng/xslt20.rng"""

    if version is not None:
        v = "".join(version.split("."))
    else:
        v = "10"

    path = os.path.join(exalt.get_plugin_path(), "rng", "xslt%s.rng" % v)
    return exalt.file_to_uri(path)


def validate_against_schema(parser, error, view, document, schema_path):
    """Validate document against schema using parser and throw error if
    validation fails."""

    current_file = view.file_name()

    # If the schema file URL is a relative URL and the file doesn't have
    # a name (as in, it hasn't been saved), bail out.
    if utils.is_relative_path(schema_path) and not current_file:
        return False

    file = utils.resolve_file_path(schema_path, current_file)

    try:
        validator = _get_validator(file, parser, file=file)
        return validate(view, document, validator)
    except (error, etree.XSLTApplyError) as e:
        return vu.show_error(view, e)


def get_validator_for_namespace(namespace):
    """Get a validator for the given namespace.

    For example, if the argument is 'http://relaxng.org/ns/structure/1.0', it
    will return a validator that can validate against a RelaxNG schema."""
    fn = validate_against_schema

    if namespace == isoschematron.RELAXNG_NS:
        return partial(fn, etree.RelaxNG, etree.RelaxNGParseError)
    elif namespace == isoschematron.XML_SCHEMA_NS:
        return partial(fn, etree.XMLSchema, etree.XMLSchemaParseError)
    elif namespace == isoschematron.SCHEMATRON_NS:
        return partial(fn, isoschematron.Schematron,
                       etree.SchematronParseError)
    elif namespace == namespaces.PRE_ISO_SCHEMATRON:
        return partial(fn, etree.Schematron, etree.SchematronParseError)


def validate_against_xml_schema(view, document, mode="namespace"):
    schema_file = _get_xml_schema_instance(document, mode)

    if schema_file is None:
        return False

    validator = get_validator_for_namespace(isoschematron.XML_SCHEMA_NS)
    return validator(view, document, schema_file)


def validate_against_dtd(view, document):
    """Validate a document against the DTD in its DOCTYPE.

    TODO: Add support for external subsets and system identifiers.
    """
    docinfo = document.docinfo
    internal_subset = docinfo.internalDTD
    system_url = docinfo.system_url

    if internal_subset is None and system_url is None:
        return False
    if internal_subset.external_id is None and system_url is not None:
        try:
            file = utils.resolve_file_path(system_url, view.file_name())
            validator = _get_validator(system_url, etree.DTD, file=file)

            return validate(view, document, validator)
        except etree.DTDParseError as e:
            return vu.show_error(view, e)
    elif internal_subset.external_id is not None:
        # <!DOCTYPE map PUBLIC "-//OASIS//DTD DITA Map//EN" "map.dtd">
        id = bytes(internal_subset.external_id, encodings.UTF8)

        try:
            validator = _get_validator(id, etree.DTD, external_id=id)
            return validate(view, document, validator)
        except etree.DTDParseError as e:
            return vu.show_error(view, e)
    else:
        # <!DOCTYPE people_list [ <!ELEMENT people_list (person)*> ]>
        try:
            return validate(view, document, internal_subset)
        except etree.DTDParseError as e:
            return vu.show_error(view, e)


def try_validate(view, document):
    if not validate_against_dtd(view, document):
        if not validate_against_xml_schema(view, document):
            if not validate_against_xml_schema(view, document, mode="URI"):
                return _validate_against_xml_models(view, document)


def validate(view, document, validator):
    try:
        validator.assertValid(document)
        return declare_valid(view)
    except etree.DocumentInvalid as e:
        if type(validator) == isoschematron.Schematron:
            message = _get_schematron_error_message(e)
        else:
            message = e
        return vu.show_error(view, message, validator.error_log[0])
    except OSError:
        vu.set_status(view, messages.SCHEMA_RESOLVE_ERROR % id)
        return False


def declare_valid(view):
    """Declare the document valid.

    Remove any highlight regions and indicate validity in status bar."""
    view.erase_regions(constants.PLUGIN_NAME)
    vu.set_status(view, messages.VALID_MARKUP)
    vu.reset_status(view)
    return True


###########
# PRIVATE #
###########


def _get_validator(id, parser, **kwargs):
    """Get a validator for the given identifier.

    Given an ID (such as a DTD public identifier or a schema URI),
    return a cached validator if there's one or make a new one if there
    isn't.

    This is probably a pretty stupid way of caching parsers. Suggestions
    appreciated."""
    validator = exalt.parser_cache.get(id) \
        if id in exalt.parser_cache else parser(**kwargs)

    exalt.parser_cache.setdefault(id, validator)
    return validator


def _get_xml_schema_instance(document, mode):
    root = document.getroot()
    xsi = root.xpath("@xsi:schemaLocation | @xsi:noNamespaceSchemaLocation",
                     namespaces={"xsi": namespaces.XSI})

    if len(xsi) == 0:
        return None

    return xsi[0].split()[0 if mode == "namespace" else -1]


def _get_xml_models(document):
    return document.xpath("/processing-instruction('xml-model')")


def _get_schematron_error_message(error):
    """Get a Schematron error message string from Schematron report.

    Schematron errors look like this:

    <svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl"
                        xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        xmlns:schold="http://www.ascc.net/xml/schematron"
                        xmlns:sch="http://www.ascc.net/xml/schematron"
                        xmlns:iso="http://purl.oclc.org/dsdl/schematron"
                        test="para" location="/section">
      <svrl:text>This section has no paragraphs</svrl:text>
    </svrl:failed-assert>

    That obviously won't fit in the status bar, so we'll extract the
    text from the <svrl:text> element. Not ideal, but will have to do for
    now."""
    xml = etree.parse(io.StringIO(str(error)))

    return xml.xpath("//svrl:text[1]//node()",
                     namespaces={"svrl": isoschematron.SVRL_NS})[0]


def _get_validator_for_extension(extension):
    if extension == ".xsd":
        return get_validator_for_namespace(isoschematron.XML_SCHEMA_NS)
    elif extension == ".rng":
        return get_validator_for_namespace(isoschematron.RELAXNG_NS)
    elif extension == ".sch":
        return get_validator_for_namespace(isoschematron.SVRL_NS)
    else:
        return None


def _validate_against_xml_models(view, document):
    """Validate a document against all xml-model PIs in the document.

    If the document is invalid, stop. If it's valid, move onto the next
    PI."""
    models = _get_xml_models(document)

    if not models:
        declare_valid(view)
        return False
    else:
        for xml_model in models:
            href = xml_model.get("href")
            namespace = xml_model.get("schematypens")

            if href is None and namespace is None:
                break
            elif href is not None and namespace is None:
                _, extension = os.path.splitext(href)

                if extension == ".dtd":
                    return validate_against_schema(
                        etree.DTD,
                        etree.DTDParseError,
                        view,
                        document,
                        href
                    )
                else:
                    validator = _get_validator_for_extension(extension)

                    if validator is not None:
                        return validator(view, document, href)
                    else:
                        return False
            else:
                validator = get_validator_for_namespace(namespace)
                return validator(view, document, href)

# Change Log

## 0.3.7
- Add support for namespace-based XML schema resolution #19

    XML schema validation now tries resolving against the namespace in the
    `xsi:schemaLocation` attribute first and only then against the URI.

- Fix disappearing validation error #20

## 0.3.6
- Improve XML syntax detection #14

    A document is now interpreted to be an XML document if the current syntax
    includes "text.xml".

## 0.3.5
- Load entities in external DTDs #15

## 0.3.4
- Clear error message for valid document #13

## 0.3.3
- Merge the `$XML_CATALOG_FILES` environment variable with the
  "xml_catalog_files" Exalt setting #11

## 0.3.2
- Add support for SYSTEM URLs in DOCTYPE declarations #8

## 0.3.1
- Add support for xml-model declarations without @schematypens #4

## 0.3.0
- Add support for canonicalizing XML #2

## 0.2.1
- Fix XSLT validation error on Windows

## 0.2.0
- Add Windows shortcuts and menus
- Add support for formatting selections
- Improve HTML formatting

## 0.1.0
- Initial release

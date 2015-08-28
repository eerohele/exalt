Exalt
=====

If you have the misfortune of having to work with XML, this is the
[Sublime Text 3][st3] plugin for you.

(Unless you're using Windows. I nearly went insane trying to compile
[lxml][lxml] for 64-bit Windows and failed miserably. Any help greatly
appreciated.)

## Features

### Validate files on the fly

Validate XML, XHTML, HTML, and XSLT files on the fly with [lxml][lxml]
against a [Document Type Definition][dtd] (DTD), an [XML schema][xsd]
(XSD), a [RelaxNG schema][rng] (RNG), or a [Schematron schema][schematron].

Exalt supports [XML catalogs][xml-catalog] via [lxml][lxml] so that you
don't need to put [unnecessary load on W3C's servers][w3c-dtd].

#### XSLT validation

If the syntax of your current file is set to [XSLT][xslt], Exalt automatically
validates the file against
[Norman Walsh's Relax NG grammars for XSLT stylesheets][ndw].

#### XSD validation

Exalt uses the `xsi:schemaLocation` or the `xsi:noNamespaceSchemaLocation`
attribute of the root element to validate against the schema defined in that
attribute.

This means Exalt can validate [Maven][maven] POM files that look like this:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>foobar</groupId>

    . . .
</project>
```

You'll probably want to set up an [XML catalog][xml-catalog] to avoid having to
fetch schemas from the internet. See **Installing** for more information.

#### `xml-model` validation

Exalt also supports the [`xml-model`][xml-model] processing instruction. That
means that you can have a processing instruction like this before the root
element of your [DITA XML 1.2][dita] document (but *after* the XML declaration,
of course):

```xml
<?xml-model href="urn:dita-ng:dita:rng:topic.rng"
            schematypens="http://relaxng.org/ns/structure/1.0"?>
```

Exalt will then validate against the schema in the `@href` attribute. It
uses the XML catalog you've set up to resolve the `@href` and the
`@schematypens` attribute to determine the the type of the schema.

You can naturally use absolute or relative paths, too:

```xml
<?xml-model href="file:///etc/xml/schemas/docbook/docbook-5.0/docbook.rng"
            schematypens="http://relaxng.org/ns/structure/1.0"?>

<?xml-model href="../docbook-5.0/xsd/docbook.xsd"
            schematypens="http://www.w3.org/2001/XMLSchema"?>
```

If your file doesn't validate, you can press `⌘ + Ctrl + E` to jump to the
validation error if it's not already in view.

### Format XML & HTML files

Press `⌘ + Ctrl + X` to reformat (pretty-print) an XML or HTML file.

Exalt tries to format non-well-formed XML files via the [libxml2][libxml2]
`recover` flag.

## Installing

1. Install Exalt via [Package Control][package-control].
2. (*Optional, but recommended*.) In `User/Exalt.sublime-settings`, set the
   path to your [XML catalog files][xml-catalog].

    For example:

    ```json
    {
      "xml_catalog_files": ["/etc/xml/catalog", "~/.schemas/catalog.xml"]
    }
    ```

    By default, the plugin uses the catalog files defined in
    `Exalt/Exalt.sublime-settings`. Those catalog files might or might not
    exist on your system.

    If you want, you can use my [`markup-schemas`][markup-schemas] repository
    to install a set of commonly used XML catalogs and schemas. Just set the
    `xml_catalog_files` setting of this plugin to point to the `catalog.xml`
    file in where you cloned the repo.

    Alternatively, you can clone[`markup-schemas`][markup-schemas] into
    `/etc/xml` and create `/etc/xml/catalog.xml` with this content:

    ```xml
    <catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
      <nextCatalog catalog="markup-schemas/catalog.xml"/>
    </catalog>
    ```
    
    If you do that, you shouldn't need to set the `xml_catalog_files` setting.
    
    **NOTE**: If you change XML catalogs in any way, you need to restart
    Sublime Text 3 for the changes to take effect.

## Known issues

- Due to libxml2 issues [#573483][libxml2-#573483], [#753970][libxml2-#753970],
  and [753997][libxml2-#753997], **none** of the available validation methods
  work for DITA 1.3 files. That's a bit of a bummer.
- Formatting HTML occasionally gives weird results (the DOCTYPE tends to
  disappear and reappear, for example).
- Formatting the same HTML file multiple times also gives weird results.
- ISO Schematron validation doesn't always report the error position correctly.

## Other caveats

- Sublime Text 3 only, OS X and Linux only (for now).
- There's probably many encoding things I didn't take into account. UTF-8
  content should work OK.
- I don't really know Python.

## TODO

- DTD validation support is incomplete.
- More unit tests are needed.

[dita]: https://en.wikipedia.org/wiki/Darwin_Information_Typing_Architecture
[dtd]: https://en.wikipedia.org/wiki/Document_type_definition
[libxml2]: http://xmlsoft.org
[libxml2-#573483]: https://bugzilla.gnome.org/show_bug.cgi?id=573483
[libxml2-#753970]: https://bugzilla.gnome.org/show_bug.cgi?id=753970
[libxml2-#753997]: https://bugzilla.gnome.org/show_bug.cgi?id=753997
[lxml]: http://lxml.de
[markup-schemas]: https://github.com/eerohele/markup-schemas
[maven]: https://maven.apache.org
[ndw]: https://github.com/ndw/xslt-relax-ng
[package-control]: https://packagecontrol.io
[py3]: https://www.python.org
[rng]: http://relaxng.org
[schematron]: http://schematron.com/
[st3]: http://www.sublimetext.com/3
[w3c-dtd]: http://www.w3.org/blog/systeam/2008/02/08/w3c_s_excessive_dtd_traffic/
[xml-catalog]: http://xmlsoft.org/catalog.html
[xml-model]: http://www.w3.org/TR/xml-model
[xsd]: http://www.w3.org/XML/Schema
[xslt]: http://www.w3.org/standards/xml/transformation

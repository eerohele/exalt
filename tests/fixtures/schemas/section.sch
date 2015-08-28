<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
   <title>Check Sections 12/07</title>
   <pattern id="section-check">
      <rule context="section">
         <assert test="title">This section has no title</assert>
         <assert test="para">This section has no paragraphs</assert>
      </rule>
   </pattern>
</schema>

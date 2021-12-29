(parser)=

# Parser

API-Reference: {py:meth}`wsgi_tools.parser`

This includes the two WSGI-apps {py:meth}`wsgi_tools.parser.JSONParser` and {py:meth}`wsgi_tools.parser.XMLParser`.

Both read the content of the request and parse it. The {py:meth}`wsgi_tools.parser.JSONParser` as a json-string and the {py:meth}`wsgi_tools.parser.XMLParser` as a xml-string.

The {py:meth}`wsgi_tools.parser.JSONParser` writes this to the attribute {py:meth}`wsgi_tools.parser.JSONParser.json_content`. The {py:meth}`wsgi_tools.parser.XMLParser` writes this to the attribute {py:meth}`wsgi_tools.parser.XMLParser.root_element`.

The raw bytes content is accessible in {py:meth}`wsgi_tools.parser.JSONParser.raw_content` or in {py:meth}`wsgi_tools.parser.XMLParser.raw_content`.

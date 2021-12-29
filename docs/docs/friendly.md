# Friendly

API-Reference: {py:meth}`wsgi_tools.friendly`

The main part of this module is the {py:meth}`wsgi_tools.friendly.FriendlyWSGI`. This is a WSGI-app which calls a function, which is more pragrammer friendly and more readable than a normal WSGI-app.

It takes a {py:meth}`wsgi_tools.friendly.Request` as an import and can return either a {py:meth}`wsgi_tools.friendly.Response` instance, a tuple of the status-code and the body or a tuple of the status-code, the body and a list of headers.

To create a {py:meth}`wsgi_tools.friendly.Response` instance you have the option to pass any of status-code, body and headers. With the method {py:meth}`wsgi_tools.friendly.Response.json_body` you can pass anything which can be procressed to a json-string (`dict`, `list`, `int`, etc.) and with the method {py:meth}`wsgi_tools.friendly.Response.xml_body` you can pass an [`xml.etree.ElementTree.Element`](https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element) or an [`xml.etree.ElementTree.ElementTree`](https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.ElementTree) which will write xml data to the body.

The status-code can either be an `int` or a `str`. The options are being described [here](https://datatracker.ietf.org/doc/html/rfc2616.html#section-10) or [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status). If you pass a `str` it should be in the format `'{status-code} {Reason}'`. If you pass an `int`, the default reason will be taken (View: {py:meth}`wsgi_tools.utils.status_codes`).

The body can either be a `str`, `bytes` or `bytearray` object or an iterable thereof. The iterable can be useful, for example if you have huge data, which you do not want to load all at once. So you can build a generator, which loads some data and yields it.

Headers can either be a dict with the names of the headers an keys and the values of the headers as values or a list of tuples `('{header-name}', '{header-value}')`.

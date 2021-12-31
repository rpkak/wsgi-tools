from __future__ import annotations

import xml.etree.ElementTree as ET



class Request:
    """A request is an object with attributes from the environ.

    This is passed to the functions.

    Args:
        environ: The environ of the wsgi call
    """

    def __init__(self, environ: WSGIEnvironment):
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.protocol = environ['SERVER_PROTOCOL']
        self.query_string = environ.get('QUERY_STRING', '')
        self.content_type = environ.get('CONTENT_TYPE')
        self.content_length = int(environ.get('CONTENT_LENGTH') or 0)
        self.scheme = environ['wsgi.url_scheme']
        self.body_stream = environ['wsgi.input']
        self.server = (environ['SERVER_NAME'], environ['SERVER_PORT'])
        self.headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                self.headers[key[5:].replace('_', '-')] = value

    @cached_property
    def body_bytes(self) -> bytes:
        return self.body_stream.read(self.content_length)

    @cached_property
    def body_string(self) -> str:
        return self.body_bytes.decode('utf-8')


def _file_iter(file_like: IO, bufsize: int):
    while(data := file_like.read(bufsize)):
        yield data
    file_like.close()


class Response:
    """A response is an object with status, body and headers of the response.

    This can be passed as a return value of the functions.

    Args:
        status (int | str, optional): The status-code of the response.
        headers (dict, optional): The headers of the response.
        body (optional): The body of the response.
    """

    def __init__(self, status: StatusCode = 200, headers: Headers = {}, body: Body = []):
        self.status = status
        self.headers = headers
        self.body = body

    def json_body(self, json: JSONValue, friendly: bool = False):
        """Sets the body to a json value:

        Args:
            json: The dict / int / bool / etc. for the json-string
        """
        self.headers['Content-Type'] = 'application/json'
        self.body = dumps(json, indent=4 if friendly else None,
                          separators=(', ', ': ') if friendly else (',', ':'))

    def xml_body(self, etree_element: Union[ET.Element, ET.ElementTree]):
        """Sets the body to an xml value:

        Args:
            etree_element (ET.Element | ET.ElementTree): The root element of the xml.
        """
        if isinstance(etree_element, ET.ElementTree):
            etree_element = etree_element.getroot()
        self.headers['Content-Type'] = 'application/json'
        self.body = ET.tostring(etree_element, encoding='utf-8')

    def file_like_body(self, file_like: IO, bufsize: int = 8192):
        """

        Args:
            file_like (file-like object): the file-like object, which can be binary and text, but has to be readable.
            bufsize (int, default: 8192): the size in bytes each iteration.
        """
        self.body = _file_iter(file_like, bufsize)


def _make_body(body: Union[str, bytes, bytearray]) -> bytes:
    if isinstance(body, str):
        return body.encode('utf-8')
    elif isinstance(body, bytearray):
        return bytes(body)
    else:
        return body


class FriendlyWSGI:
    """The WSGI-App, which forwards the request to the functions.

    Args:
        func: the more programmer friendly function.
    """

    def __init__(self, func: Callable[[Request], Union[Response, tuple[StatusCode, Body], tuple[StatusCode, Body, Headers]]]):
        self.func = func

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        response = self.func(Request(environ))

        if isinstance(response, Response):
            status, body, headers = response.status, response.body, response.headers
        elif len(response) == 2:
            status, body = response
            headers = {}
        elif len(response) == 3:
            status, body, headers = response

        status = get_status_code_string(status)

        if isinstance(headers, dict):
            headers = [header for header in headers.items()]

        start_response(status, headers)

        if isinstance(body, (str, bytes, bytearray)):
            body = [_make_body(body)]
        else:
            body = (_make_body(d) for d in body)
        return body

"""This makes WSGI more programmer friendly.

This module includes a WSGI-app with forwards the wsgi-app to a function,
which is simpler than a normal WSGI-app function:

It has a request as an argument and can return either a response or a tuple
of status-code and body or a tuple of status-code, body and headers.

Examples:
    >>> def foo(request):
    ...     print(request.body_string)
    ...     response = Response(status=201)
    ...     response.json_body({
    ...         'id': 0
    ...     })
    ...     return response
    ...
    >>> app0 = FriendlyWSGI(foo)
    >>>
    >>> def bar(request):
    ...     return 200, request.body_bytes
    ...
    >>> app1 = FriendlyWSGI(bar)
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from json import dumps
from typing import TYPE_CHECKING

from .utils import get_status_code_string

# from functools import cached_property

cached_property = property

if not TYPE_CHECKING:
    try:
        from functools import cached_property
    except ImportError:
        pass

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from typing import (BinaryIO, Dict, List, Optional, TextIO, Tuple, Union,
                        cast)

    from _typeshed.wsgi import StartResponse, WSGIEnvironment

    from .utils import JSONValue

    Headers = Union[List[Tuple[str, str]], Dict[str, str]]
    Headers.__doc__ = """A header has to be a list of tuples or a dict.
    """

    Body = Union[str, bytes, bytearray,
                 Iterable[Union[str, bytes, bytearray]]]
    Body.__doc__ = """A body has to be a string, bytes or bytearray object or an iterable thereof.
    """

    StatusCode = Union[str, int]
    StatusCode.__doc__ = """A status-code has to be a string or an int.
    """


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
        self.body_stream: BinaryIO = environ['wsgi.input']
        self.server = (environ['SERVER_NAME'], environ['SERVER_PORT'])
        self.headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                self.headers[key[5:].replace('_', '-')] = value
        self._body_bytes: Optional[bytes] = None

    # @cached_property
    # def body_bytes(self) -> bytes:
    #     return self.body_stream.read(self.content_length)

    @property
    def body_bytes(self) -> bytes:
        if self._body_bytes is None:
            self._body_bytes = self.body_stream.read(self.content_length)
        return self._body_bytes

    @cached_property
    def body_string(self) -> str:
        return self.body_bytes.decode('utf-8')


def _file_iter(file_like: Union[BinaryIO, TextIO], bufsize: int) -> Iterator[Union[bytes, str]]:
    while True:
        data = file_like.read(bufsize)
        if not data:
            break
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
        self.headers = headers if isinstance(headers, dict) else {name: value for name, value in headers}
        self.body = body

    def json_body(self, json: JSONValue, friendly: bool = False) -> None:
        """Sets the body to a json value:

        Args:
            json: The dict / int / bool / etc. for the json-string
        """
        self.headers['Content-Type'] = 'application/json'
        self.body = dumps(json, indent=4 if friendly else None,
                          separators=(', ', ': ') if friendly else (',', ':'))

    def xml_body(self, etree_element: Union[ET.Element, ET.ElementTree]) -> None:
        """Sets the body to an xml value:

        Args:
            etree_element (ET.Element | ET.ElementTree): The root element of the xml.
        """
        if isinstance(etree_element, ET.ElementTree):
            etree_element = etree_element.getroot()
        self.headers['Content-Type'] = 'application/json'
        self.body = ET.tostring(etree_element, encoding='utf-8')

    def file_like_body(self, file_like: Union[BinaryIO, TextIO], bufsize: int = 8192) -> None:
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

    def __init__(self, func: Callable[[Request], Union[Response, Tuple[StatusCode, Body], Tuple[StatusCode, Body, Headers]]]):
        self.func = func

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        response = self.func(Request(environ))

        status: StatusCode
        body: Body
        headers: Headers

        if isinstance(response, Response):
            status, body, headers = response.status, response.body, response.headers
        elif len(response) == 2:
            if TYPE_CHECKING:
                response = cast(Tuple[StatusCode, Body], response)
            status, body = response
            headers = []
        else:
            if TYPE_CHECKING:
                response = cast(Tuple[StatusCode, Body, Headers], response)
            status, body, headers = response

        status = get_status_code_string(status)

        if isinstance(headers, dict):
            headers = [header for header in headers.items()]

        start_response(status, headers)

        final_body: Iterable[bytes]

        if isinstance(body, (str, bytes, bytearray)):
            final_body = [_make_body(body)]
        else:
            final_body = (_make_body(d) for d in body)
        return final_body

from __future__ import annotations

import xml.etree.ElementTree as ET
from functools import cached_property
from json import dumps
from typing import TYPE_CHECKING

from .utils import get_status_code_string



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

"""This module includes WSGI-apps, which parse content and call another WSGI-app.

Do not use

.. code:: python

    environ['wsgi.input'].read()

except in these parsers.

If you want the raw bytes content, you can use:

.. code:: python

    parser.raw_content

"""
from __future__ import annotations

import threading
import xml.etree.ElementTree as ET
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING

from .error import HTTPException

if TYPE_CHECKING:
    from collections.abc import Iterable

    from _typeshed.wsgi import StartResponse, WSGIApplication, WSGIEnvironment

    from .utils import JSONValue


class JSONParser:
    """A WSIG app, which parses json from the content.

    Args:
        app: The WSGI-app, the parser will forward.
    """

    @property
    def raw_content(self) -> bytes:
        """bytes: the raw content of the body
        """
        return self.request_data.raw_content

    @property
    def json_content(self) -> JSONValue:
        """the json content
        """
        return self.request_data.json_content

    def __init__(self, app: WSGIApplication):
        self.app = app
        self.request_data = threading.local()

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        if 'CONTENT_TYPE' in environ:
            if 'json' in environ['CONTENT_TYPE'].split('/')[1].split('+'):
                self.request_data.raw_content = environ['wsgi.input'].read(
                    int(environ.get('CONTENT_LENGTH', 0)))
                try:
                    self.request_data.json_content = loads(
                        self.request_data.raw_content)
                except JSONDecodeError:
                    raise HTTPException(422, message='Invalid JSON')
                return self.app(environ, start_response)
            else:
                raise HTTPException(
                    415, message='Only json content is allowed.')
        else:
            raise HTTPException(400, message='Body required')


class XMLParser:
    """A WSIG app, which parses xml from the content.

    Args:
        app: The WSGI-app, the parser will forward.
    """

    @property
    def raw_content(self) -> bytes:
        """bytes: the raw content of the body
        """
        return self.request_data.raw_content

    @property
    def root_element(self) -> ET.Element:
        """ET.Element: the root element of the xml element-tree
        """
        return self.request_data.root_element

    def __init__(self, app: WSGIApplication):
        self.app = app
        self.request_data = threading.local()

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        if 'CONTENT_TYPE' in environ:
            if 'xml' in environ['CONTENT_TYPE'].split('/')[1].split('+'):
                self.request_data.raw_content = environ['wsgi.input'].read(
                    int(environ.get('CONTENT_LENGTH', 0)))
                try:
                    self.request_data.root_element = ET.fromstring(
                        self.request_data.raw_content)
                except ET.ParseError:
                    raise HTTPException(422, message='Invalid XML')
                return self.app(environ, start_response)
            else:
                raise HTTPException(
                    415, message='Only xml content is allowed.')
        else:
            raise HTTPException(400, message='Body required')

import xml.etree.ElementTree as ET
from functools import cached_property
from json import JSONDecodeError, dumps, loads

from wsgi_tools.error import HTTPException

from .utils import get_status_code_string


class Request:
    def __init__(self, environ):
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
    def body_bytes(self):
        return self.body_stream.read(self.content_length)

    @cached_property
    def body_string(self):
        return self.body_bytes.decode('utf-8')


class Response:
    def __init__(self, status=200, headers={}, body=[]):
        self.status = status
        self.headers = headers
        self.body = body

    def json_body(self, json, friendly=False):
        self.headers['Content-Type'] = 'application/json'
        self.body = dumps(json, indent=4 if friendly else None,
                          separators=(', ', ': ') if friendly else (',', ':'))

    def xml_body(self, etree_element):
        if isinstance(etree_element, ET.ElementTree):
            etree_element = etree_element.getroot()
        self.headers['Content-Type'] = 'application/json'
        self.body = ET.tostring(etree_element, encoding='utf-8')


def _make_body(body):
    if isinstance(body, str):
        return body.encode('utf-8')
    elif isinstance(body, bytearray):
        return bytes(body)
    else:
        return body


class FriendlyWSGI:
    def __init__(self, func):
        self.func = func

    def __call__(self, environ, start_response):
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

from functools import cached_property
from json import dumps, loads

from .utils import status_codes


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.method = environ['REQUEST_METHOD']
        self.path = environ['PATH_INFO']
        self.content_length = int(environ.get('CONTENT_LENGTH') or 0)
        self.routing_args = environ.get('wsgi_tools.routing.args', [])
        self.scheme = environ['wsgi.url_scheme']
        self.query_string = environ.get('QUERY_STRING', '')
        self.content_type = environ.get('CONTENT_TYPE', 'text/plain')
        self.body_stream = environ['wsgi.input']

    @cached_property
    def body_bytes(self):
        return self.body_stream.read(self.content_length)

    @cached_property
    def body_string(self):
        return self.body_bytes.decode('utf-8')

    @cached_property
    def body_json(self):
        if len(self.content_type.split('/')) == 1 or 'json' in self.content_type.split('/')[1].split('+'):
            return loads(self.body_bytes)
        else:
            raise ValueError('Content-Type is not JSON')

    def get_header(self, name):
        return self.environ.get('HTTP_' + name.upper().replace('-', '_'))


class Response:
    def __init__(self, status=200, headers={}, body=[]):
        self.status = status
        self.headers = headers
        self.body = body

    def json_body(self, json, friendly=False):
        self.headers['Content-Type'] = 'application/json'
        self.body = dumps(json, indent=4 if friendly else None,
                          separators=(', ', ': ') if friendly else (',', ':'))


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

        if status in status_codes:
            status = '%s %s' % (status, status_codes[status])

        if isinstance(headers, dict):
            headers = [header for header in headers.items()]

        start_response(status, headers)

        if isinstance(body, (str, bytes, bytearray)):
            body = [_make_body(body)]
        else:
            body = (_make_body(d) for d in body)
        return body

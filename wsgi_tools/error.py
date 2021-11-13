from abc import ABCMeta, abstractmethod
from json import dumps
from sys import exc_info
from traceback import print_exc

from .utils import get_status_code_string, status_codes


class HTTPException(Exception):
    def __init__(self, code, message=None, exc_info=None):
        Exception.__init__(self)
        self.code = code
        self.message = message
        self.exc_info = exc_info


class ErrorHandler(metaclass=ABCMeta):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as e:
            if not isinstance(e, HTTPException):
                print_exc()
                e = HTTPException(500, message='A server error occurred. Please contact an administrator.', exc_info=exc_info())
            body, headers = self.handle(e)
            status = get_status_code_string(e.code)
            start_response(status, headers, e.exc_info)
            return body

    @abstractmethod
    def handle(self, e):
        pass


class JSONErrorHandler(ErrorHandler):
    def __init__(self, *args, friendly=False, **kwargs):
        ErrorHandler.__init__(self, *args, **kwargs)
        self.friendly = friendly

    def handle(self, e):
        error = {
            'code': int(e.code[:3]) if isinstance(e.code, str) else e.code,
            'error': e.code[4:] if isinstance(e.code, str) else status_codes[e.code]
        }
        if e.message is not None:
            error['message'] = e.message
        return ([dumps(error, indent=4 if self.friendly else None,
                       separators=(', ', ': ') if self.friendly else (',', ':')).encode('utf-8')], [('Content-Type', 'application/json')])

# class PlainTextErrorHandler(ErrorHandler):
#     def handle(self, e):
#         return (str(e), [('Content-Type', 'text/plain')])


class HTMLErrorHandler(ErrorHandler):
    def handle(self, e):
        status_code_bytes = get_status_code_string(e.code).encode('utf-8')
        return ([b'<html><head><title>%s</title></head><body><h1>%s</h1>%s</body></html>' % (
                status_code_bytes,
                status_code_bytes,
                b'<p>%s</p>' % e.message.encode('utf-8') if e.message else b''
                )], [('Content-Type', 'text/html')])

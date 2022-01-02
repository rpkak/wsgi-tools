"""Catches any Exception and returns that an error occured.

This is required by many other modules of this package.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from json import dumps
from sys import exc_info
from traceback import print_exc
from typing import TYPE_CHECKING

from .utils import get_status_code_string, status_codes

if TYPE_CHECKING:
    from collections.abc import Iterable
    from sys import _OptExcInfo
    from typing import List, Optional, Tuple, Union

    from _typeshed.wsgi import StartResponse, WSGIApplication, WSGIEnvironment


class HTTPException(Exception):
    """A Exception which says, what status-code and what message should be displayed.

    Args:
        code (int | str): The status-code of this Exception
        message (str, optional): The message of the error.
        exc_info (optional): sys.exc_info() if raised because of another exception.
        headers (list(tuple), optional): specific headers for this exception
    """

    def __init__(self, code: Union[int, str], message: Optional[str] = None, exc_info: Optional[_OptExcInfo] = None, headers: List[Tuple[str, str]] = []):
        Exception.__init__(self)
        self.code = code
        self.message = message
        self.exc_info = exc_info
        self.headers = headers


class ErrorHandler(metaclass=ABCMeta):
    """A WSGI-app which executes another WSGI-App and handles exceptions, if they occur.

    If the exception is no HTTPException, an HTTPException with the code 500, the message
    :code:`'A server error occurred. Please contact an administrator.'` and the exc_info will be taken.

    This is an abstract class. The handle method needs to be overwritten.

    Args:
        app: The WSGI-app, which is called by the ErrorHandler
    """

    def __init__(self, app: WSGIApplication):
        self.app = app

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        try:
            return self.app(environ, start_response)
        except BaseException as e:
            if not isinstance(e, HTTPException):
                print_exc()
                e = HTTPException(
                    500, message='A server error occurred. Please contact an administrator.', exc_info=exc_info())
            body, headers = self.handle(e)
            headers.extend(e.headers)
            status = get_status_code_string(e.code)
            start_response(status, headers, e.exc_info)
            return body

    @abstractmethod
    def handle(self, e: HTTPException) -> Tuple[Iterable[bytes], List[Tuple[str, str]]]:
        """Abstract methed, which has an exception as an arg and returns a body and a list of headers.
        """
        pass


class JSONErrorHandler(ErrorHandler):
    """An ErrorHandler which returns the error in the json-body.

    Args:
        friendly (bool, optional): If true, the output will be human readable, else (default), the output will be minimal.
        *args: The args of ErrorHandler
        *kwargs: The kwargs of ErrorHandler
    """

    def __init__(self, app: WSGIApplication, friendly: bool = False):
        ErrorHandler.__init__(self, app)
        self.friendly = friendly

    def handle(self, e: HTTPException) -> Tuple[Iterable[bytes], List[Tuple[str, str]]]:
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
    """An ErrorHandler which returns the error in viewable html format.
    """

    def handle(self, e: HTTPException) -> Tuple[Iterable[bytes], List[Tuple[str, str]]]:
        status_code_bytes = get_status_code_string(e.code).encode('utf-8')
        return ([b'<html><head><title>%s</title></head><body><h1>%s</h1>%s</body></html>' % (
                status_code_bytes,
                status_code_bytes,
                b'<p>%s</p>' % e.message.encode('utf-8') if e.message else b''
                )], [('Content-Type', 'text/html')])

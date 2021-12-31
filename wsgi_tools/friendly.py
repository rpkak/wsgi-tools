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
from functools import cached_property
from json import dumps

from .utils import get_status_code_string

if False:
    from collections.abc import Callable, Iterable
    from typing import IO, TypeAlias, Union

    from _typeshed.wsgi import StartResponse, WSGIEnvironment

    from .utils import JSONValue

    Headers: TypeAlias = Union[list[tuple[str, str]], dict[str, str]]
    Headers.__doc__ = """A header has to be a list of tuples or a dict.
    """

    Body: TypeAlias = Union[str, bytes, bytearray,
                            Iterable[Union[str, bytes, bytearray]]]
    Body.__doc__ = """A body has to be a string, bytes or bytearray object or an iterable thereof.
    """

    StatusCode: TypeAlias = Union[str, int]
    Body.__doc__ = """A status-code has to be a string or an int.
    """

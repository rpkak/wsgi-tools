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

from collections.abc import Callable, Iterable
from typing import IO, TypeAlias, Union

from _typeshed.wsgi import StartResponse, WSGIEnvironment

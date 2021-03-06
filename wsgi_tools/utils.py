"""Utilities of the :py:meth:`wsgi_tools` package.

Contains some general constants and functions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, List, Union

    # https://github.com/python/mypy/issues/731
    # JSONValue: TypeAlias = Union[Dict[str, 'JSONValue'],
    #                              List['JSONValue'], str, int, float, bool, None]

    _AnyJSONValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
    JSONValue = Union[Dict[str, _AnyJSONValue],
                      List[_AnyJSONValue], str, int, float, bool, None]
    del _AnyJSONValue
    JSONValue.__doc__ = """TypeAlias: A type, which represents all possible JSON values.
    """

status_codes = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    103: 'Early Hints',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    208: 'Already Reported',
    226: 'IM Used',
    300: 'Multiple Choice',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Range Not Satisfiable',
    417: 'Expectation Failed',
    418: 'I\'m a teapot',
    421: 'Misdirected Request',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    425: 'Too Early',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    451: 'Unavailable For Legal Reasons',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    508: 'Loop Detected',
    510: 'Not Extended',
    511: 'Network Authentication Required',
}
"""dict: All HTTP status_codes

The keys are the codes as ints and the values are the strings without numbers.
"""


def get_status_code_string(code: Union[int, str]) -> str:
    """Returns the status as a string.

    Args:
        code (int | str): The int or string of this status_code

    Returns:
        str: The status_code as a string

    Examples:
        >>> get_status_code_string(404)
        '404 Not Found'
        >>> get_status_code_string('200 foo')
        '200 foo'
    """
    if isinstance(code, int):
        return '%s %s' % (code, status_codes[code])
    else:
        return code

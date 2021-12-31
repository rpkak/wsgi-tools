"""This module includes WSGI-apps, which parse content and call another WSGI-app.

Compared to wsgi_tools.parser this also includes a json-filter
so that you can not pass any json you want to the parser, but only json that works for your app.

Do not use

.. code:: python

    environ['wsgi.input'].read()

except in this parser.

If you want the raw bytes content, you can use:

.. code:: python

    parser.raw_content


"""
from __future__ import annotations

import threading
from json import JSONDecodeError, loads
from typing import TYPE_CHECKING

from .error import HTTPException

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Optional, TypeAlias, Union

    from _typeshed.wsgi import StartResponse, WSGIApplication, WSGIEnvironment

    from .utils import JSONValue

    Filter: TypeAlias = Callable[[JSONValue], tuple[bool, str]]
    Filter.__doc__ = """A function, which works as filter.
    """


class Number:
    """A filter class, which checks if values are numbers (ints or floats) and if they are in a specific range.

    Number is not directly a filter, but has to be constructed.

    Args:
        min (int | float, optional): The minimum value.
        max (int | float, optional): The maximum value.
        require_int (bool): If False (default) floats are allowed, if True they are not.
    """

    def __init__(self, min: Optional[Union[int, float]] = None, max: Optional[Union[int, float]] = None, require_int: bool = False):
        self.min = min
        self.max = max
        self.require_int = require_int

    def __call__(self, value: JSONValue) -> tuple[bool, str]:
        if self.require_int and value.__class__ != int:
            return False, 'expected int, found \'%s\' of type %s' % (value, value.__class__.__name__)
        elif value.__class__ != float and value.__class__ != int:
            return False, 'expected number, found \'%s\' of type %s' % (value, value.__class__.__name__)
        elif self.min is not None and self.min > value:
            return False, 'expected number bigger than %s, found %s' % (self.min, value)
        elif self.max is not None and self.max < value:
            return False, 'expected number smaler than %s, found %s' % (self.min, value)
        else:
            return True, ''


def Boolean(value: JSONValue) -> tuple[bool, str]:
    """A Filter, which checks if values are booleans.

    Boolean is directly a filter.
    """
    return value.__class__ == bool, 'expected boolean, found \'%s\' of type %s' % (value, value.__class__.__name__)


def String(value: JSONValue) -> tuple[bool, str]:
    """A Filter, which checks if values are strings.

    String is directly a filter.
    """
    return value.__class__ == str, 'expected string, found \'%s\' of type %s' % (value, value.__class__.__name__)


class Array:
    """A filter class, which checks if values are lists and if their content is correct.

    List is not directly a filter, but has to be constructed.

    Args:
        filter: The filter, which filters the contents of the list.
    """

    def __init__(self, filter: Filter):
        self.filter = filter

    def __call__(self, value: JSONValue) -> tuple[bool, str]:
        if value.__class__ == list:
            for i, e in enumerate(value):
                check, reason = self.filter(e)
                if not check:
                    return False, '%s: %s' % (i, reason)
            return True, ''
        else:
            return False, 'expected list, found \'%s\' of type %s' % (value, value.__class__.__name__)


class Options:
    """A filter class, which checks if the content matches one of multiple filters

    Options is not directly a filter, but has to be constructed.

    Args:
        options: The filters, where one of them should match.
    """

    def __init__(self, *options: Filter):
        self.options = options

    def __call__(self, value: JSONValue) -> tuple[bool, str]:
        reasons = []
        for filter in self.options:
            check, reason = filter(value)
            if check:
                return True, ''
            else:
                reasons.append(reason)
        return False, 'Value not allowed (%s).' % ' or '.join(reasons)


class Object:
    """A filter class, which checks if values are objects and if their content is correct.

    Object is not directly a filter, but has to be constructed.

    Args:
        entries (dict): a dict with the keys of the object as keys and the filters of
            the values of the object as values. If some entries are optional, the values should be a tuple
            with the filter and True.
        ignore_more (bool, optional): If False (default), objects do not match if they
            have more entries than the filter.
    """

    def __init__(self, entries: dict[str, Filter], ignore_more: bool = False):
        self.entries = {}
        for key in entries:
            if isinstance(entries[key], tuple):
                self.entries[key] = entries[key]
            else:
                self.entries[key] = (entries[key], False)

        self.ignore_more = ignore_more

    def __call__(self, value: JSONValue) -> tuple[bool, str]:
        if value.__class__ == dict:
            value_keys = list(value)
            for key in self.entries:
                filter, optional = self.entries[key]
                if key in value_keys:
                    check, reason = filter(value[key])
                    if not check:
                        return False, '%s: %s' % (key, reason)
                    value_keys.remove(key)
                elif not optional:
                    return False, 'entry with key \'%s\' required' % key
            if len(value_keys) == 0 or self.ignore_more:
                return True, ''
            else:
                return False, 'unsupported key \'%s\'' % value_keys[0]
        else:
            return False, 'expected object, found \'%s\' of type %s' % (value, value.__class__.__name__)


def Null(value: JSONValue) -> tuple[bool, str]:
    """A Filter, which checks if values equals null.

    Null is directly a filter.
    """
    return value is None, 'expected null, found \'%s\' of type %s' % (value, value.__class__.__name__)


class FilteredJSONParser:
    """A WSIG app, which parses json from the content.

    Args:
        app: The WSGI-app, the parser will forward.
        filter: The filter, which the json-content should match.
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

    def __init__(self, app: WSGIApplication, filter: Filter):
        self.app = app
        self.filter = filter
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
                check, reason = self.filter(self.request_data.json_content)
                if check:
                    return self.app(environ, start_response)
                else:
                    raise HTTPException(400, reason)
            else:
                raise HTTPException(
                    415, message='Only json content is allowed.')
        else:
            raise HTTPException(400, message='Body required')

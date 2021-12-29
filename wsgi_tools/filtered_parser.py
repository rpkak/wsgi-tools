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
import threading
from json import JSONDecodeError, loads

from .error import HTTPException


class Int:
    """A filter class, which checks if values are ints and if they are in a specific range.

    Int is not directly a filter, but has to be constructed.

    Args:
        min (int, optional): The minimum value.
        max (int, optional): The maximum value.
    """

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, value):
        if value.__class__ != int:
            return False, 'expected int, found \'%s\' of type %s' % (value, value.__class__.__name__)
        elif self.min is not None and self.min > value:
            return False, 'expected int bigger than %s, found %s' % (self.min, value)
        elif self.max is not None and self.max < value:
            return False, 'expected int smaler than %s, found %s' % (self.min, value)
        else:
            return True, ''


class Float:
    """A filter class, which checks if values are floats and if they are in a specific range.

    Float is not directly a filter, but has to be constructed.

    Args:
        min (float, optional): The minimum value.
        max (float, optional): The maximum value.
    """

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, value):
        if value.__class__ != float:
            return False, 'expected float, found \'%s\' of type %s' % (value, value.__class__.__name__)
        elif self.min is not None and self.min > value:
            return False, 'expected float bigger than %s, found %s' % (self.min, value)
        elif self.max is not None and self.max < value:
            return False, 'expected float smaler than %s, found %s' % (self.min, value)
        else:
            return True, ''


def Boolean(value):
    """A Filter, which checks if values are booleans.

    Boolean is directly a filter.
    """
    return value.__class__ == bool, 'expected boolean, found \'%s\' of type %s' % (value, value.__class__.__name__)


def String(value):
    """A Filter, which checks if values are strings.

    String is directly a filter.
    """
    return value.__class__ == str, 'expected string, found \'%s\' of type %s' % (value, value.__class__.__name__)


class List:
    """A filter class, which checks if values are lists and if their content is correct.

    List is not directly a filter, but has to be constructed.

    Args:
        filter: The filter, which filters the contents of the list.
    """

    def __init__(self, filter):
        self.filter = filter

    def __call__(self, value):
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

    def __init__(self, *options):
        self.options = options

    def __call__(self, value):
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

    def __init__(self, entries, ignore_more=False):
        self.entries = {}
        for key in entries:
            if isinstance(entries[key], tuple):
                self.entries[key] = entries[key]
            else:
                self.entries[key] = (entries[key], False)

        self.ignore_more = ignore_more

    def __call__(self, value):
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


class FilteredJSONParser:
    """A WSIG app, which parses json from the content.

    Args:
        app: The WSGI-app, the parser will forward.
        filter: The filter, which the json-content should match.
    """

    @property
    def raw_content(self):
        """bytes: the raw content of the body
        """
        return self.request_data.raw_content

    @property
    def json_content(self):
        """the json content
        """
        return self.request_data.json_content

    def __init__(self, app, filter):
        self.app = app
        self.filter = filter
        self.request_data = threading.local()

    def __call__(self, environ, start_response):
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

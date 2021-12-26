from json import loads, JSONDecodeError
from .error import HTTPException


class Int:
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
    return value.__class__ == bool, 'expected boolean, found \'%s\' of type %s' % (value, value.__class__.__name__)


def String(value):
    return value.__class__ == str, 'expected string, found \'%s\' of type %s' % (value, value.__class__.__name__)


class List:
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
    def __init__(self, app, filter):
        self.app = app
        self.filter = filter
        self.raw_content = None
        self.json_content = None

    def __call__(self, environ, start_response):
        if 'CONTENT_TYPE' in environ:
            if 'json' in environ['CONTENT_TYPE'].split('/')[1].split('+'):
                self.raw_content = environ['wsgi.input'].read(
                    int(environ.get('CONTENT_LENGTH', 0)))
                try:
                    self.json_content = loads(self.raw_content)
                except JSONDecodeError:
                    raise HTTPException(422, message='Invalid JSON')
                check, reason = self.filter(self.json_content)
                if check:
                    return self.app(environ, start_response)
                else:
                    raise HTTPException(400, reason)
            else:
                raise HTTPException(
                    415, message='Only json content is allowed.')
        else:
            raise HTTPException(400, message='Body required')
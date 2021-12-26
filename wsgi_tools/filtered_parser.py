from json import loads, JSONDecodeError
from .error import HTTPException

class Int:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, value):
        if value.__class__ != int:
            return False
        elif self.min is not None and self.min > value:
            return False
        elif self.max is not None and self.max < value:
            return False
        else:
            return True


class Float:
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, value):
        if value.__class__ != float:
            return False
        elif self.min is not None and self.min > value:
            return False
        elif self.max is not None and self.max < value:
            return False
        else:
            return True


def Boolean(value):
    return value.__class__ == bool


def String(value):
    return value.__class__ == str


class List:
    def __init__(self, type):
        self.type = type

    def __call__(self, value):
        if value.__class__ == list:
            return all(self.type(e) for e in value)
        else:
            return False

class Options:
    def __init__(self, *options):
        self.options = options

    def __call__(self, value):
        return any(func(value) for func in self.options)

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
                func, optional = self.entries[key]
                if key in value_keys:
                    if not func(value[key]):
                        return False
                    value_keys.remove(key)
                elif not optional:
                    return False
            return len(value_keys) == 0 or self.ignore_more
        else:
            return False

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
                if self.filter(self.json_content):
                    return self.app(environ, start_response)
                else:
                    raise HTTPException(400, 'JSON does not meet requirements.')
            else:
                raise HTTPException(
                    415, message='Only json content is allowed.')
        else:
            raise HTTPException(400, message='Body required')

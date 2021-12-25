from abc import ABCMeta, abstractmethod

from wsgi_tools.error import HTTPException


class Rule(metaclass=ABCMeta):
    @abstractmethod
    def get_exception(self):
        pass

    @abstractmethod
    def check(self, environ, value):
        pass

    def clear(self):
        pass


class PathRule(Rule):
    def __init__(self):
        self.args = []

    def check(self, environ, value):
        args = []
        string = True
        path = environ['PATH_INFO']
        for i in range(len(value)):
            if string:
                if path[:len(value[i])] == value[i]:
                    path = path[len(value[i]):]
                else:
                    return False
            else:
                if i+1 == len(value):
                    content = path
                    path = ''
                else:
                    content_end = path.find(value[i+1])
                    if content_end == -1:
                        return False
                    else:
                        content = path[:content_end]
                        path = path[content_end:]
                func = value[i]
                try:
                    arg = func(content)
                except ValueError:
                    return False
                args.append(arg)
            string = not string
        if path != '':
            return False
        else:
            self.args = args
            return True

    def get_exception(self):
        return HTTPException(404, message='Path not found')


class MethodRule(Rule):
    def check(self, environ, value):
        return value == environ['REQUEST_METHOD']

    def get_exception(self):
        return HTTPException(405)


METHOD_RULE = MethodRule()


class ContentTypeRule(Rule):
    def check(self, environ, value):
        if environ.get('CONTENT_TYPE') is None:
            return value is None
        elif value is None:
            return False
        if '/' in value:
            return value == environ.get('CONTENT_TYPE', 'text/plain')
        else:
            return value in environ.get('CONTENT_TYPE', 'text/plain').split('/')[1].split('+')

    def get_exception(self):
        return HTTPException(415, message='Unsupported Content-Type')


CONTENT_TYPE_RULE = ContentTypeRule()


class Router:
    def __init__(self, rules, routes):
        self.rules = rules
        self.routes = routes

    def __call__(self, environ, start_response):
        routes = list(self.routes)
        for i, rule in enumerate(self.rules):
            routes = [route for route in routes if rule.check(
                environ, route[i])]
            if len(routes) == 0:
                raise rule.get_exception()
        return self.routes[routes[0]](environ, start_response)

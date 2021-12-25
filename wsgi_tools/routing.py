from wsgi_tools.error import HTTPException


def _check_path(router, environ, value):
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
        router.path_args = args
        return True


PATH = (_check_path, 404)


def _check_method(router, environ, value):
    return value == environ['REQUEST_METHOD']


METHOD = (_check_method, 405)


def _check_content_type(router, environ, value):
    if environ.get('CONTENT_TYPE') is None:
        return value is None
    elif value is None:
        return False
    if '/' in value:
        return value == environ.get('CONTENT_TYPE', 'text/plain')
    else:
        return value in environ.get('CONTENT_TYPE', 'text/plain').split('/')[1].split('+')


CONTENT_TYPE = (_check_content_type, 415)


class Router:
    def __init__(self, rules, routes):
        self.rules = rules
        self.routes = routes
        self.path_args = None

    def __call__(self, environ, start_response):
        routes = list(self.routes)
        for i, (rule_func, code) in enumerate(self.rules):
            routes = [route for route in routes if rule_func(self, environ, route[i])]
            if len(routes) == 0:
                self.path_args = None
                raise HTTPException(code)
        # for route in self.routes:
        #     if all(rule(self, environ, value) for rule, value in zip(self.rules, route)):
        #         response = self.routes[route](environ, start_response)
        #         self.path_args = None
        #         return response
        self.path_args = None
        return self.routes[routes[0]](environ, start_response)

"""With routing you can forward your request to specific WSGI-apps.

There are two main classes in this module: Router and Rule

The Router is the WSGI-app, which uses rules to know, to which WSGI-app it should forward.

You construct the Router with a list of all Rules you use and with an arg for each route and rule.

The Rule defindes if the request and the (arg of this rule in the) route match.

Example:
    >>> from wsgi_tools.routing import CONTENT_TYPE_RULE, METHOD_RULE, PathRule, Router

    >>> path_rule = PathRule()

    >>> app = Router(
    ...     [path_rule, METHOD_RULE, CONTENT_TYPE_RULE],
    ...     {
    ...         (('/create',), 'POST', 'json'): create_app,
    ...         (('/', int, '/options'), 'GET', None): options_app
    ...     }
    ... )

"""

from abc import ABCMeta, abstractmethod

from wsgi_tools.error import HTTPException


class Rule(metaclass=ABCMeta):
    """A Rule is an object, which defines if request can be forwarded to a route.

    Some Rules also store data of the current request which are accessable
    from the code which is executed at this request.
    """

    @abstractmethod
    def get_exception(self):
        """If no route matches this rule, an exception has to be thrown.

        Returns:
            HTTPException: The exception which will be thrown, if no route supports thie rule.
        """
        pass

    @abstractmethod
    def check(self, environ, value):
        """The Method, which controles, whether an request and a route are matching this rule.

        Args:
            environ (dict): A WSGI-environ
            value: the value of this rule for a route

        Returns:
            bool: True if environ and value are matching, False otherwise
        """
        pass


class PathRule(Rule):
    """A Rule, which controlls the path of the request.

    The arg you have to specifiy in each route is a tuple or a list.
    This tuple or list has to begin with a string.

    The simplest arg is a tuple, which is only one string.

    `('/',)` is the root document.

    `('/hello',)` is `http://{host}/hello`

    You get an generic path, if you include callables, which have a `str` as the only arg
    and raise an ValueError if the input is wrong.

    Examples for these callables are `int` and `float`, but you can create your own functions as well.

    If is not allowed, that two of these callables are directly after each others.

    `('/', str, '/foo')` for `/bar/foo` and `args` is `['bar']` or `/hello/foo` and `args` is `['hello']`.

    `('/id/', int, '/user/', str, '/create')` for `/id/321/user/root/create` and `args` is `[321, 'root']`.

    Attributes:
        args (list): The list of the generic parts of the path.
    """

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
    """A rule which checks if the http methods match.

    The arg you have to specifiy in each route is a `str` representing the http-method
    (e.g. `'GET'`, `'POST'` or `'DELETE'`).

    Note:
        You can use the constant `METHOD_RULE`, because this rule does not have any attributes.
    """

    def check(self, environ, value):
        return value == environ['REQUEST_METHOD']

    def get_exception(self):
        return HTTPException(405)


METHOD_RULE = MethodRule()
"""A rule which checks if the http methods match.

The arg you have to specifiy in each route is a `str` representing the http-method
(e.g. `'GET'`, `'POST'` or `'DELETE'`).
"""


class ContentTypeRule(Rule):
    """A rule which checks if the content_types match.

    The arg you have to specifiy in each route is a `str` which represents the content-type or
    `None` if you don't expect content in this route (e.g. for a `GET` request).

    If the arg is a `str` and includes a `/`, the rule will match, if arg and content-type match exactly.

    If the arg is a `str`, but it doesn't includes any `/`, the rule will match, if the arg is located
    at any place after the `/` in the content type.

    For example:

    `json` matches `application/json`, `application/foo+json`, `hello/foo+json+bar`, etc.

    `application/json` only matches `application/json`.

    Note:
        You can use the constant `CONTENT_TYPE_RULE`, because this rule does not have any attributes.
    """

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
"""A rule which checks if the content_types match.

The arg you have to specifiy in each route is a `str` which represents the content-type or
`None` if you don't expect content in this route (e.g. for a `GET` request).

If the arg is a `str` and includes a `/`, the rule will match, if arg and content-type match exactly.

If the arg is a `str`, but it doesn't includes any `/`, the rule will match, if the arg is located
at any place after the `/` in the content type.

For example:

`json` matches `application/json`, `application/foo+json`, `hello/foo+json+bar`, etc.

`application/json` only matches `application/json`.
"""


class Router:
    """The WSGI-app, which forwards requests on their environ.

    Args:
        rules (list(Rule)): A list of the rules you want to use.
        routes (dict): A dict representing the routes. A route is an dict-entry with a tuple or list
            with the args for all rules for this route as the key and the WSGI-app the router shoult
            forward to as the value.
    """

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

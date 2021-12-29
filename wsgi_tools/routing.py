"""With routing you can forward your request to specific WSGI-apps.

There are two main classes in this module: :py:meth:`Router` and :py:meth:`Rule`

The :py:meth:`Router` is the WSGI-app, which uses rules to identify, to which WSGI-app it should forward.

You construct the :py:meth:`Router` with a list of all rules you use and with an arg for each route and rule.

The :py:meth:`Rule` defines if the request and the (arg of this rule in the) route match.

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
    """A Rule is an object, which defines if requests can be forwarded to a route.

    Some Rules also store data of the current request which are accessible
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
        """The Method, which controls, whether a request and a route are matching this rule.

        Args:
            environ (dict): A WSGI-environ
            value: the value of this rule for a route

        Returns:
            bool: True if environ and value are matching, False otherwise
        """
        pass


class PathRule(Rule):
    """A Rule, which controls the path of the request.

    The arg you have to specifiy in each route is a tuple or a list.
    This tuple or list has to begin with a string.

    The simplest arg is a tuple, which is only one string.

    :code:`('/',)` is the root document.

    :code:`('/hello',)` is :code:`http://{host}/hello`

    You get an generic path, if you include callables, which have a :code:`str` as the only arg
    and raise a ValueError if the input is wrong.

    Examples for these callables are :code:`int` and :code:`float`, but you can create your own functions as well.

    It is not allowed that two of these callables are directly follow upon each other.

    :code:`('/', str, '/foo')` for :code:`/bar/foo` and :code:`args` is :code:`['bar']` or :code:`/hello/foo` and :code:`args` is :code:`['hello']`.

    :code:`('/id/', int, '/user/', str, '/create')` for :code:`/id/321/user/root/create` and :code:`args` is :code:`[321, 'root']`.

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
    """A rule which checks whether the http methods match.

    The arg you have to specifiy in each route is a :code:`str` representing the http-method
    (e.g. :code:`'GET'`, :code:`'POST'` or :code:`'DELETE'`).

    Note:
        You can use the constant :py:meth:`METHOD_RULE`, because this rule does not have any attributes.
    """

    def check(self, environ, value):
        return value == environ['REQUEST_METHOD']

    def get_exception(self):
        return HTTPException(405)


METHOD_RULE = MethodRule()
"""A rule which checks whether the http methods match.

The arg you have to specifiy in each route is a :code:`str` representing the http-method
(e.g. :code:`'GET'`, :code:`'POST'` or :code:`'DELETE'`).
"""


class ContentTypeRule(Rule):
    """A rule which checks whether the content_types match.

    The arg you have to specifiy in each route is a :code:`str` which represents the content-type or
    :code:`None` if you do not expect content in this route (e.g. for a :code:`GET` request).

    If the arg is a :code:`str` and includes a :code:`/`, the rule will match, if arg and content-type match exactly.

    If the arg is a :code:`str`, but it does not includes any :code:`/`, the rule will match, if the arg is located
    at any place after the :code:`/` in the content type.

    For example:

    :code:`json` matches :code:`application/json`, :code:`application/foo+json`, :code:`hello/foo+json+bar`, etc.

    :code:`application/json` only matches :code:`application/json`.

    Note:
        You can use the constant :py:meth:`CONTENT_TYPE_RULE`, because this rule does not have any attributes.
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
"""A rule which checks whether the content_types match.

The arg you have to specifiy in each route is a :code:`str` which represents the content-type or
:code:`None` if you do not expect content in this route (e.g. for a :code:`GET` request).

If the arg is a :code:`str` and includes a :code:`/`, the rule will match, if arg and content-type match exactly.

If the arg is a :code:`str`, but it does not includes any :code:`/`, the rule will match, if the arg is located
at any place after the :code:`/` in the content type.

For example:

:code:`json` matches :code:`application/json`, :code:`application/foo+json`, :code:`hello/foo+json+bar`, etc.

:code:`application/json` only matches :code:`application/json`.
"""


class Router:
    """The WSGI-app, which forwards requests on their environ.

    Args:
        rules (list(Rule)): A list of the rules you want to use.
        routes (dict): A dict representing the routes. A route is a dict-entry with a tuple or list
            with the args for all rules for this route as the key and the WSGI-app the router should
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

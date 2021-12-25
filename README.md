# WSGI-Tools

A collection of WSGI packages

## Usage

See: example.py

### ErrorHandler

The error handler is a WSGI app which calls another WSGI app.

If that WSGI app raises a `wsgi_tools.error.HTTPException`, the error code and an optional message will be returńed.

If that WSGI app raises a normal Exception, the error code `500` will be returńed.

Import:

```python
from wsgi_tools.error import ErrorHandler, JSONErrorHandler, HTMLErrorHandler
```

To use the `ErrorHandler` you have to overwrite the abstract `handle` method or use the prebuild `JSONErrorHandler` or `HTMLErrorHandler`.

```python
app = JSONErrorHandler(app0)
```

### Friedly

With this you can serve easy-to-use functions over WSGI.

```python
def app0(request):
    data = request.body_json
    response = do_something(data)
    return 200, response
```

### Router

The router is a WSGI app which reads the path of the request and calls another corresponding WSGI app.

Import:

```python
from wsgi_tools.routing import Router
```

Create the Router:

The first argument of `Router` is the `list` of rules you want to use.

A rule an instance of an subclass of `wsgi_tools.routing.Rule`.

The order of these rules is important, because you don't want to throw an `405 Method Not Allowed` error if there are no endpoints which match one of the endpoint and the method.

So the path-checking rule must be before the method checking rule.

There are premade rules for matching path, method and content-type:

```python
from wsgi_tools.routing import PathRule, METHOD_RULE, CONTENT_TYPE_RULE
```

The second argument is the `dict` with tuples as keys, which represent the args for the rules and wsgi apps as keys.

```python
from wsgi_tools.routing import Router, PathRule, METHOD_RULE, CONTENT_TYPE_RULE

path_rule = PathRule()

app = Router(
    [path_rule, METHOD_RULE, CONTENT_TYPE_RULE],
    {
        (('/create',), 'POST', 'json'): create_app,
        (('/', int, '/options'), 'GET', None): options_app
    }
)
```

If you send a `POST` request to `/create` and the content-type is `*/json`, `*/*+json`, `*/json+*` or `*/*+json+*`, `create_app` will be called.

If you send a `GET` request to `/3/options`, `options_app` will be called and `path_rule.args` will be `[3]`.

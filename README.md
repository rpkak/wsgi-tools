# WSGI-Tools

A collection of WSGI packages

## Usage

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

```python
app = Router(
    {
        ('POST', ('/create')): app0,
        ('GET', ('/', int, '/options')): app1
    }
)
```

If you send a `POST` request to `/create`, `app0` will be called.

If you send a `GET` request to `/3/options`, `app1` will be called and `environ['wsgi_tools.routing.args']` will be `[3]`. If you are using `wsgi_tools.friendly`, `request.routing_args` will be `[3]`.

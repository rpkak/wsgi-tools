class FriendlyWSGI:
    """The WSGI-App, which forwards the request to the functions.

    Args:
        func: the more programmer friendly function.
    """

    def __init__(self, func: Callable[[Request], Union[Response, tuple[StatusCode, Body], tuple[StatusCode, Body, Headers]]]):
        self.func = func

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        response = self.func(Request(environ))

        if isinstance(response, Response):
            status, body, headers = response.status, response.body, response.headers
        elif len(response) == 2:
            status, body = response
            headers = {}
        elif len(response) == 3:
            status, body, headers = response

        status = get_status_code_string(status)

        if isinstance(headers, dict):
            headers = [header for header in headers.items()]

        start_response(status, headers)

        if isinstance(body, (str, bytes, bytearray)):
            body = [_make_body(body)]
        else:
            body = (_make_body(d) for d in body)
        return body

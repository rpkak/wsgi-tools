# Basic Auth

API-Reference: {py:meth}`wsgi_tools.basic_auth`

```{warning}
Do not use this, if your connection is not secure. The password will only be `base64` encoded, which is decodable by anyone.
```

This includes the WSGI-app {py:meth}`wsgi_tools.basic_auth.BasicAuth`. It first checks if the request is authenticated. If it is, it simply calls the WSGI-app, specified in the constructor. If not, the response will tell this to the client.

To create a {py:meth}`wsgi_tools.basic_auth.BasicAuth` instance you have to specify not only the app, but a function called `is_correct` as well. This will be called with the two args. The first arg is the user as a `str` and the second arg is the password as a `str`. This should return a `True`, if this login information is correct and `False` otherwise.



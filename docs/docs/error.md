# Error

API-Reference: {py:meth}`wsgi_tools.error`

This module includes the abstract WSGI-app {py:meth}`wsgi_tools.error.ErrorHandler`. It simply calls the WSGI-app, specified in the constructor. If a {py:meth}`wsgi_tools.error.HTTPException` occurs, the {py:meth}`wsgi_tools.error.ErrorHandler` will handle it using the abstract {py:meth}`wsgi_tools.error.ErrorHandler.handle` method. If any other exception occurs, the {py:meth}`wsgi_tools.error.ErrorHandler` will create a `500 Internal Server Error` and handle it.

There are two implementations of {py:meth}`wsgi_tools.error.ErrorHandler` in this module, but you can do your own as well:

- {py:meth}`wsgi_tools.error.JSONErrorHandler`:

  The handle method returns a json-string of an object, with entries for `code`, `error` and `message`, if the message was set in the {py:meth}`wsgi_tools.error.HTTPException`.

  The internal server error thrown by the handler, will be:

  ```json
  {
      "code": 500, 
      "error": "Internal Server Error", 
      "message": "A server error occurred. Please contact an administrator."
  }
  ```

- {py:meth}`wsgi_tools.error.HTMLErrorHandler`:

  The handle method returns an html-string, which is human readable in the browser.

  The internal server error thrown by the handler, will be:

  ```html
  <html><head><title>500 Internal Server Error</title></head><body><h1>500 Internal Server Error</h1><p>A server error occurred. Please contact an administrator.</p></body></html>
  ```


  ```{raw} html
  <p>Here as an iframe:</p>
  <iframe style="width: 100%;background-color: #FFFFFF;" src="data:text/html,<html><head><title>500 Internal Server Error</title></head><body><h1>500 Internal Server Error</h1><p>A server error occurred. Please contact an administrator.</p></body></html"></iframe>
  ```

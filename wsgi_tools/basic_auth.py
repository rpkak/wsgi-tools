"""Basic Auth implementation in WSGI.
"""

import threading
from base64 import b64decode

from .error import HTTPException


class BasicAuth:
    """A WSGI-app which asks you to authenticate if you are not and forwards the request otherwise.

    Args:
        app: The WSGI-app with authenticated access only
        is_correct: a function which processes username and the passwd, whether it is
            correct or wrong.
        realm (str, optional): String describing, what is forbidden without authentication.
    """

    @property
    def user(self):
        """str: The user which is logged in in this request.
        """
        return self.request_data.user

    def __init__(self, app, is_correct, realm='Access to content'):
        self.app = app
        self.is_correct = is_correct
        self.realm = realm
        self.request_data = threading.local()

    def __call__(self, environ, start_response):
        if 'HTTP_AUTHORIZATION' in environ and environ['HTTP_AUTHORIZATION'].startswith('Basic '):
            base64_string = environ['HTTP_AUTHORIZATION'][6:]
            try:
                byte_string = b64decode(base64_string)
                string = byte_string.decode('utf-8')
                i = string.find(':')
                if i != -1:
                    self.request_data.user = string[:i]
                    passwd = string[i+1:]
                    if self.is_correct(self.request_data.user, passwd):
                        return self.app(environ, start_response)
                    else:
                        raise HTTPException(
                            401, message='Wrong user or password')
                else:
                    raise HTTPException(
                        400, message='Authentication not processable')
            except ValueError:
                raise HTTPException(
                    400, message='Authentication not processable')
        else:
            headers = [('WWW-Authenticate', 'Basic realm="%s"' % self.realm)]
            raise HTTPException(
                401, message='Authentication required', headers=headers)

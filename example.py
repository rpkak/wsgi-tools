from typing import Tuple

from wsgi_tools.basic_auth import BasicAuth
from wsgi_tools.error import JSONErrorHandler
from wsgi_tools.filtered_parser import (FilteredJSONParser, Number, Object,
                                        String)
from wsgi_tools.friendly import FriendlyWSGI, Request, Response
from wsgi_tools.routing import CONTENT_TYPE_RULE, METHOD_RULE, PathRule, Router

path_rule = PathRule()


def create(request: Request) -> Response:
    print(create_app_parser.json_content)
    response = Response(201)
    response.json_body({
        'id': 0,
        'you': create_app_auth.user
    })
    return response


def get_options(request: Request) -> Tuple[int, str]:
    if path_rule.args[0] == 0:
        return 200, 'some options'
    else:
        return 400, 'No options'


def index(request: Request) -> Response:
    response = Response()
    response.file_like_body(open('example.py'))
    return response


create_app = FriendlyWSGI(create)
options_app = FriendlyWSGI(get_options)
index_app = FriendlyWSGI(index)

create_app_parser = FilteredJSONParser(create_app, Object(
    {
        # Int bigger than 0
        'id': Number(min=0, require_int=True),
        # the True in this tuple says that this arg is optional
        'description': (String, True)
    }
))


def check_access(user: str, passwd: str) -> bool:  # Connection to salting, hashing and a database
    return user == 'root' and passwd == 'secret'


create_app_auth = BasicAuth(create_app_parser, check_access,
                            realm='Ability to create something')

router_app = Router(
    [path_rule, METHOD_RULE, CONTENT_TYPE_RULE],
    {
        (('/create',), 'POST', 'json'): create_app_auth,
        (('/', int, '/options'), 'GET', None): options_app,
        (('/',), 'GET', None): index_app
    }
)

app = JSONErrorHandler(router_app)

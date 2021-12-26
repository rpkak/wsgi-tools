from wsgi_tools.error import JSONErrorHandler
from wsgi_tools.friendly import FriendlyWSGI, Request, Response
from wsgi_tools.routing import CONTENT_TYPE_RULE, METHOD_RULE, PathRule, Router
from wsgi_tools.filtered_parser import FilteredJSONParser, Int, Object, String, Float, Options

path_rule = PathRule()


def create(request: Request):
    print(create_app_parser.json_content)
    response = Response(201)
    response.json_body({
        'id': 0
    })
    return response


def get_options(request: Request):
    if path_rule.args[0] == 0:
        return 200, 'some options'
    else:
        return 400, 'No options'


create_app = FriendlyWSGI(create)
options_app = FriendlyWSGI(get_options)

create_app_parser = FilteredJSONParser(create_app, Object(
    {
        # Either int or float bigger than 0
        'id': Options(Int(min=0), Float(min=0)),
        # the True in this tuple says, that this arg is optional
        'description': (String, True)
    }
))

app = Router(
    [path_rule, METHOD_RULE, CONTENT_TYPE_RULE],
    {
        (('/create',), 'POST', 'json'): create_app_parser,
        (('/', int, '/options'), 'GET', None): options_app
    }
)

app = JSONErrorHandler(app)

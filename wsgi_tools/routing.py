def match_pattern(pattern, test):
    args = []
    string = True
    for i in range(len(pattern)):
        if string:
            if test[:len(pattern[i])] == pattern[i]:
                test = test[len(pattern[i]):]
            else:
                return False, []
        else:
            if i+1 == len(pattern):
                content = test
                test = ''
            else:
                content_end = test.find(pattern[i+1])
                if content_end == -1:
                    return False, []
                else:
                    content = test[:content_end]
                    test = test[content_end:]
            func = pattern[i]
            try:
                value = func(content)
            except ValueError:
                return False, []
            args.append(value)
        string = not string
    if test != '':
        return False, []
    else:
        return True, args


class Router:
    def __init__(self, routes, not_found):
        self.routes = routes
        self.not_found = not_found

    def __call__(self, environ, start_response):
        for method, path in self.routes:
            if method == environ['REQUEST_METHOD']:
                match, args = match_pattern(path, environ['PATH_INFO'])
                if match:
                    environ['wsgi_tools.routing.args'] = args
                    return self.routes[(method, path)](environ, start_response)

        return self.not_found(environ, start_response)

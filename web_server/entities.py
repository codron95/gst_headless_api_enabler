import json


class Request(object):

    def __init__(self, path, method, data=None, **kwargs):
        self.path = path
        self.method = method
        self.data = data
        self.meta = kwargs

        if not self.data:
            self.data = {}


class Response(object):

    def __init__(self, code=200, message=None):
        self.code = code
        self.message = message if message is not None else ""
        self.headers = {"Content-Type": "text/plain"}

    def add_header(self, header):
        self.headers.update(header)

    def get_content(self):
        return self.message

    def __str__(self):
        return "{code}: {message}".format(
            code=self.code,
            message=self.message
        )


class JsonResponse(Response):

    def __init__(self, code=200, message=None, data=None, errors=None):
        super(JsonResponse, self).__init__(code, message)
        self.data = data if data is not None else {}
        self.errors = errors if errors is not None else []
        self.headers = {"Content-Type": "application/json"}

    def get_content(self):
        content = {}
        content['message'] = self.message
        content['data'] = self.data
        content['errors'] = self.errors
        return json.dumps(content)


class URL(object):

    def __init__(self, controller, **kwargs):

        self.controller = controller
        self.allowed_methods = []
        if kwargs['allowed_methods']:
            self.allowed_methods = kwargs['allowed_methods']

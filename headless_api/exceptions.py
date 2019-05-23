class LoginException(Exception):

    def __init__(self, message, code):

        super(LoginException, self).__init__(message)
        self.code = code

    def __str__(self):

        return "{code}: {message}".format(
            code=self.code,
            message=super(LoginException, self).__str__()
        )

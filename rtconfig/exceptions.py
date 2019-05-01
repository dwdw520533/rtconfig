import json


class BaseConfigException(Exception):
    """
    Baseclass for all HTTP exceptions.
    """
    def __init__(self, code=None, description=None, **options):
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description
        self.options = options

    code = None
    description = None

    def __str__(self):
        return self.description.format(**self.options)

    def get_message(self):
        return json.dumps({
            'code': self.code,
            'error_msg': str(self)
        })


class ProjectNoFoundException(BaseConfigException):
    code = 404
    description = "Project {config_name} config manager not exist."


class ConnectException(BaseConfigException):
    code = 404
    description = "Connection happened unknown exception: \n{exp_info}"

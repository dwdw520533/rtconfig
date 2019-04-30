class BaseBackend:
    def read(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

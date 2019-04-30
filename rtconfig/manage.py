import json
import attr
from datetime import datetime
from rtconfig.utils import to_hash, strftime, convert_dt
from rtconfig.config import JSON_FILE_DIRECTORY
from rtconfig.backend.base import BaseBackend
from rtconfig.backend.json_file import JsonFileBackend

MT_NO_CHANGE = 'nochange'
MT_CHANGED = 'changed'


JSON = {
    "name": "dw",
    "password": "@int 99999",
    "host": "server.com",
    "port": "@int 8080",
    "alist": ["item1", "item2", 23],
    "service": {
      "url": "service.com",
      "port": 80,
      "auth": {
        "password": "qwerty",
        "test": 1234
      }
    }
}


class ConfigManager:
    _backend_class = JsonFileBackend
    _notify_handler = set()

    def __init__(self, project_name, backend_class=None, notify_handler=None):
        if backend_class is not None:
            self._backend_class = backend_class
        assert issubclass(self._backend_class, BaseBackend)
        self.project_name = project_name
        self.store_backend = self._backend_class(JSON_FILE_DIRECTORY, self.project_name)
        self._source_data = {}
        self.notify_handler = notify_handler
        self.refresh()

    def refresh(self):
        self._source_data = self.store_backend.read()

    @property
    def source_data(self):
        return self._source_data

    @source_data.setter
    def source_data(self, value):
        self._source_data = value

    @property
    def hash_code(self):
        return to_hash(self._source_data)

    async def update_config(self):
        self.store_backend.write(self.source_data)
        self.refresh()
        for handler in self._notify_handler:
            await handler(self)

    @classmethod
    def notify(cls, func):
        cls._notify_handler.add(func)
        return func

    def config_message(self):
        return Message(
            MT_CHANGED,
            self.project_name,
            self.hash_code,
            self.source_data
        ).to_string()


@attr.s
class Message:
    message_type = attr.ib(validator=attr.validators.instance_of(str))
    project_name = attr.ib(validator=attr.validators.instance_of(str))
    hash_code = attr.ib(validator=attr.validators.instance_of(str))
    data = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))
    context = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))
    lut = attr.ib(default=None, converter=convert_dt)

    def to_dict(self):
        return dict(
            message_type=self.message_type,
            project_name=self.project_name,
            hash_code=self.hash_code,
            data=self.data,
            context=self.context,
            lut=strftime(self.lut)
        )

    def to_string(self):
        return json.dumps(self.to_dict())


if __name__ == '__main__':
    import asyncio
    # conf = ConfigManager('demo')
    # conf.source_data = JSON
    # asyncio.get_event_loop().run_until_complete(conf.update_config())
    msg = Message('1', 'dw', '1', lut='2018-01-01 00:00:00')
    print(msg)

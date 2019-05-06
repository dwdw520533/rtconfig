import os
import json
import asyncio
import logging
import websockets
import threading
import importlib
from rtconfig.manager import Message


def config_logging(file_name=None):
    log_formatter = logging.Formatter("%(asctime)s: %(message)s")
    root_logger = logging.getLogger()

    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


class RtConfigClient:
    def __init__(self, config_name, ws_url, logger=None, ping_interval=5,
                 retry_interval=5, config_module=None, daemon=True):
        self._data = None
        self._thread = None
        self.config_name = config_name
        self.ws_url = ws_url
        self.hash_code = ''
        self.ping_interval = ping_interval
        self.retry_interval = retry_interval
        self.logger = logger or logging.getLogger(__name__)
        self.connect_url = os.path.join(self.ws_url, 'connect')
        self._config_module = None
        self.daemon = daemon

        if config_module is not None:
            self.config_to_module(config_module)

    @property
    def data(self):
        return self._data

    def no_change(self, message):
        pass

    def changed(self, message):
        self.logger.info('Config changed: ', message)
        self.hash_code = message.hash_code
        self._data = message.data
        if self._config_module:
            for key, value in self._data.items():
                self._config_module[key] = value

    @asyncio.coroutine
    def connect(self):
        ws = yield from websockets.connect(self.connect_url)
        self.logger.info('Connect to rtconfig server success.')
        while True:
            send_msg = Message(
                "no_change",
                self.config_name,
                self.hash_code,
                context={'pid': os.getpid()}
            )
            yield from ws.send(send_msg.to_string())
            received_msg = yield from ws.recv()
            json_data = json.loads(received_msg)
            try:
                message = Message(**json_data)
                getattr(self, message.message_type)(message)
            except AttributeError:
                pass
            except TypeError as ex:
                raise Exception(json_data.get('error_msg', str(ex)))
            finally:
                yield from asyncio.sleep(self.ping_interval)

    @asyncio.coroutine
    def loop(self):
        while True:
            try:
                yield from self.connect()
            except (websockets.ConnectionClosed, ConnectionRefusedError):
                self.logger.info('Retry to connect server: %s.' % self.ws_url)
            except Exception as ex:
                self.logger.error(str(ex))
            finally:
                yield from asyncio.sleep(self.retry_interval)

    def run_forever(self):
        config_logging()

        def loop_async(loop):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.loop())

        try:
            main_loop = asyncio.get_event_loop()
            self._thread = threading.Thread(
                target=loop_async, args=(main_loop, ))
            self._thread.daemon = self.daemon
            self._thread.start()
        except (KeyboardInterrupt, SystemExit):
            self._thread.join()
            self._thread = None

    def config_to_module(self, config_module):
        if isinstance(config_module, str):
            config_module = importlib.import_module(config_module)
        self._config_module = config_module


if __name__ == '__main__':
    import time
    from rtconfig.config import WS_SERVER
    config_logging()
    client = RtConfigClient('demo', WS_SERVER)
    client.run_forever()
    while True:
        print('=====start')
        time.sleep(1)

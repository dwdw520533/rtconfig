import os
import json
import asyncio
import logging
import websockets
import threading
import traceback
import importlib
from rtconfig.manager import Message


class RtConfigClient:
    def __init__(self, config_name, ws_url, logger=None, ping_interval=5,
                 retry_interval=5, config_module=None):
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

    async def connect(self):
        async with websockets.connect(self.connect_url) as ws:
            while True:
                send_msg = Message(
                    "no_change",
                    self.config_name,
                    self.hash_code,
                    context={'pid': os.getpid()}
                )
                await ws.send(send_msg.to_string())
                message = Message(**json.loads(await ws.recv()))
                try:
                    getattr(self, message.message_type)(message)
                except AttributeError:
                    pass
                await asyncio.sleep(self.ping_interval)

    async def loop(self):
        while True:
            try:
                await self.connect()
            except (websockets.ConnectionClosed, ConnectionRefusedError):
                self.logger.info('retry to connect server: %s.' % self.ws_url)
            except Exception as ex:
                self.logger.error(str(ex))
                self.logger.error(traceback.format_exc())
            finally:
                await asyncio.sleep(self.retry_interval)

    def run_forever(self):

        def loop_async():
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.loop())

        try:
            self._thread = threading.Thread(target=loop_async)
            self._thread.daemon = True
            self._thread.start()
        except (KeyboardInterrupt, SystemExit):
            self._thread.join()
            self._thread = None

    def config_to_module(self, config_module):
        if isinstance(config_module, str):
            config_module = importlib.import_module(config_module)
        self._config_module = config_module

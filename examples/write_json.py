import os
import asyncio
from rtconfig.config import STORE_DIRECTORY
from rtconfig.manage import ConfigManager


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

if __name__ == '__main__':
    directory = os.path.join('../rtconfig', STORE_DIRECTORY)
    conf = ConfigManager('demo', store_directory=directory)
    conf.source_data = JSON
    asyncio.get_event_loop().run_until_complete(conf.update_config())

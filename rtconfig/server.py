import json
import asyncio
from alita import Alita
from rtconfig.config import SERVER_INTERVAL
from rtconfig.manage import ConfigManager, Message

app = Alita('rtconfig')
connected = {}
connected_message = {}
config_store_state = {}


def get_config_store(project_name):
    if project_name not in config_store_state:
        config_store_state[project_name] = ConfigManager(project_name)
    return config_store_state[project_name]


def register_connected_ws(message, ws):
    if message.project_name not in connected:
        connected.setdefault(message.project_name, set())
    if ws not in connected[message.project_name]:
        connected[message.project_name].add(ws)
    connected_message[ws] = message


def remove_connected_ws(project_name, ws):
    try:
        connected[project_name].remove(ws)
        if ws in connected_message:
            del connected_message[ws]
    except KeyError:
        pass


@ConfigManager.notify
async def notify_changed(config_store):
    config_store_state[config_store.project_name] = config_store
    clients = connected.get(config_store.project_name) or []
    for client in clients:
        message = connected_message.get(client)
        if not (message and message.project_name == config_store.project_name):
            continue
        if config_store.hash_code != message.hash_code:
            continue
        await client.send(config_store.config_message())


@app.websocket('/connect')
async def index(request, ws):
    message = None
    while True:
        try:
            while True:
                message = Message(**json.loads(await ws.recv()))
                print('===recv:', message)
                register_connected_ws(message, ws)
                conf = get_config_store(message.project_name)
                if message.hash_code != conf.hash_code:
                    await ws.send(conf.config_message())
                else:
                    await ws.send(message.to_string())
                await asyncio.sleep(SERVER_INTERVAL)
        except Exception as ex:
            raise ex
        finally:
            remove_connected_ws(message.project_name, ws)


@app.route('/change')
async def change(request):
    project_name = request.args['project_name']
    conf = get_config_store(project_name)
    await conf.update_config()
    return conf.source_data


@app.route('/')
async def connect_clients(request):
    project_name = request.args['project_name']
    clients = connected.get(project_name) or []
    return [dict(id=id(c), **connected_message[c].to_dict()) for c in clients]


if __name__ == '__main__':
    app.run(host='192.168.5.65')

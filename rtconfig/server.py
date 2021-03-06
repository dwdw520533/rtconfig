import asyncio
import traceback
import itertools
from alita import Alita
from rtconfig.manager import *
from rtconfig.config import SERVER_INTERVAL, WS_SERVER
from alita import render_template
from websockets import ConnectionClosed
from rtconfig.exceptions import BaseConfigException, ConnectException, \
    GlobalApiException, ProjectExistException

logger = logging.getLogger(__name__)
app = Alita('rtconfig', static_folder='static')


@app.error_handler(GlobalApiException)
def api_exception_handler(request, exc):
    return {'code': 1, 'msg': exc.msg, 'data': {}}


@app.websocket('/connect')
async def client_connect(request, ws):
    message = None
    while True:
        try:
            message = Message(request=request, **json.loads(await ws.recv()))
            register_connected_ws(message, ws)
            conf = get_config_store(message.config_name)
            if message.hash_code != conf.hash_code:
                await ws.send(conf.config_message(request))
            else:
                await ws.send(message.to_string())
        except BaseConfigException as ex:
            logger.exception(str(ex))
            await ws.send(ex.get_message())
        except (asyncio.CancelledError, ConnectionClosed) as ex:
            remove_connected_ws(message.config_name, ws)
            raise ex
        except Exception as ex:
            logger.exception(traceback.format_exc())
            await ws.send(ConnectException(exp_info=str(ex)).get_message())
        finally:
            await asyncio.sleep(SERVER_INTERVAL)


@app.route('/change')
async def change(request):
    config_name = request.args['config_name']
    conf = get_config_store(config_name)
    await conf.update_config()
    return conf.source_data


@app.route('/')
async def page_config_list(request):
    return await render_template(request, 'config_list.html')


@app.route('/config_client')
async def page_config_client(request):
    config_name = request.args.get('config_name') or ''
    ws_url = '%s/ws/config/client?config_name=%s' % (WS_SERVER, config_name)
    return await render_template(request, 'config_client.html', ws_url=ws_url)


@app.route('/config/list')
async def config_list(request):
    return {
        'code': 0,
        'data': [i.display_info() for i in config_store_state.values()]
    }


@app.route('/config', methods=['GET', 'POST', 'PUT'])
async def config_detail(request):
    config_name = request.args['config_name']
    if request.method == "POST":
        try:
            config_store = await create_config_store(config_name)
        except ProjectExistException:
            raise GlobalApiException('配置名称已存在')
    else:
        try:
            config_store = config_store_state[config_name]
        except KeyError:
            raise GlobalApiException('配置名称不存在')
        if request.method == "PUT":
            if not request.json:
                raise GlobalApiException('配置数据不能为空')
            config_store.source_data = request.json
            await config_store.update_config()
    return {
        'code': 0,
        "data": config_store.display_info()
    }


@app.route('/config/client')
async def config_clients(request):
    config_name = request.args.get('config_name')
    if config_name:
        clients = connected.get(config_name) or []
        return {
            'code': 0,
            "data": [connected_message[c].to_dict(indent=4) for c in clients]
        }
    else:
        return {
            'code': 0,
            "data": list(itertools.chain(*[[
                connected_message[c].to_dict(indent=4) for c in i]
                for i in connected.values()]))
        }


@app.websocket('/ws/config/client')
async def ws_config_clients(request, ws):
    config_name = request.args.get('config_name')
    while True:
        if config_name:
            clients = connected.get(config_name) or []
            data = [connected_message[c].to_dict(indent=4) for c in clients]
        else:
            data = list(itertools.chain(*[[
                    connected_message[c].to_dict(indent=4) for c in i]
                    for i in connected.values()]))
        await ws.send(json.dumps(data))
        await asyncio.sleep(1)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

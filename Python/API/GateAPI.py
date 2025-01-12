import hashlib
import hmac
import json
import time
from decimal import Decimal
from typing import cast

from PySide6.QtCore import qDebug, Slot, QUrl, QUrlQuery, QTimer
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtQml import QmlElement, QmlSingleton

from Python.API.ExchangeApi import ExchangeApiBase, ApiTaskItem
from Python.Constants import SqlCurrency, SqlOrder
from Python.utils import setup_header, get_timestamp

# Base Url
API_URL = 'https://api.gateio.ws'
SERVER_TIMESTAMP_URL = '/api/v4/spot/time'
SYMBOL_INFO_URL = '/api/v4/spot/currency_pairs'
# http header
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}


def gen_signed_header(api_key, api_secret, method, url, timestamp_s, query_string=None, payload_string=None):
    sha = hashlib.sha512()
    sha.update((payload_string or "").encode('utf-8'))
    hashed_payload = sha.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, timestamp_s)
    sign = hmac.new(api_secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': api_key, 'Timestamp': str(timestamp_s), 'SIGN': sign}


def gen_websocket_request(api_key, api_secret, channel, event='subscribe', payload=None):
    time_s = int(time.time())
    sign_str = f'channel={channel}&event={event}&time={time_s}'
    sign = hmac.new(api_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha512).hexdigest()
    request = {
        "time": time_s,
        "channel": channel,
        "event": event,
        "auth": {
            "method": "api_key",
            "KEY": api_key,
            "SIGN": sign
        }
    }
    if payload is not None:
        request.update({'payload': payload})
    return json.dumps(request)

def gen_websocket_spot_login(api_key, api_secret):
    time_ms = get_timestamp()
    time_s = int(time_ms / 1000)
    channel = 'spot.login'
    event = 'api'
    req_param = ''
    sign_str = f'{event}\n{channel}\n{req_param}\n{time_s}'
    sign = hmac.new(api_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha512).hexdigest()
    request = {
        "time": time_s,
        "channel": channel,
        "event": 'api',
        "payload": {
            "req_id": str(time_ms),
            "api_key": api_key,
            "signature": sign,
            "timestamp": str(time_s)
        }
    }
    return json.dumps(request)

def gen_websocket_spot_order_place(req_id, base, quote, side, price:Decimal, quantity:Decimal, timestamp):
    time_ms = max(get_timestamp(), timestamp)
    time_s = int(time_ms / 1000)
    request = {
        "time": time_s,
        "channel": "spot.order_place",
        "event": "api",
        "payload": {
            "req_id": str(req_id),
            "req_param": {
                "text": 't-apiv4-ws',
                "currency_pair": (base + '_' + quote).upper(),
                "type": "limit",
                "side": side.lower(),
                "amount": str(quantity),
                "price": str(price)
            }
        }
    }
    return json.dumps(request)

QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
@QmlSingleton
class GateApi(ExchangeApiBase):

    def __init__(self):
        super().__init__()
        self.exchange = "Gate.io"
        self.params = None
        self.set_additional_delay(0)
        self.traces = {}

    def rest_open_event(self):
        self.balances.clear()
        if self.database:
            self.database.clear_order()

        # balance
        self._get_initial_balance()
        # order
        self._get_initial_order()

    def websocket_open_event(self):
        self.open_websocket('wss://api.gateio.ws/ws/v4/')

    def websocket_connected_event(self):
        self._websocket_login()
        # balance
        request = gen_websocket_request(self._api_key, self._api_secret, 'spot.balances', 'subscribe')
        self.send_websocket_message(request)
        # order
        request = gen_websocket_request(self._api_key, self._api_secret, 'spot.orders', 'subscribe', ['!all'])
        self.send_websocket_message(request)

    def websocket_disconnected_event(self):
        QTimer.singleShot(30000, self.websocket_open_event)

    def read_websocket_message(self, message: str):
        json_data = json.loads(message)
        # spot trading
        if 'header' in json_data:
            if json_data['header']['channel'] == 'spot.login':
                self._read_websocket_login(json_data)
            elif json_data['header']['channel'] == 'spot.order_place':
                self._read_websocket_order_ack(json_data)
        else:   # subscription
            channel = json_data['channel']
            if channel == 'spot.pong':
                self._read_websocket_pong(json_data)
            # balance
            if channel == 'spot.balances':
                self._read_websocket_balances(json_data)
            # order
            elif channel == 'spot.orders':
                self._read_websocket_orders(json_data)

    def ping(self):
        ts = int(time.time())
        ping = {"time": ts, "channel": "spot.ping"}
        request = json.dumps(ping)
        self.mark_ping()
        self.send_websocket_message(request)

    def update_currencies(self):
        url = API_URL + SYMBOL_INFO_URL
        request = QNetworkRequest(url)
        setup_header(HEADERS, request)
        reply = self.http_manager.get(request)
        reply.finished.connect(self._on_all_currencies_replied)

    def order_task_2s_countdown_event(self, task_id):
        pass

    def order_task_event(self, task_id):
        print("Order_task_event:", get_timestamp(), self.server_timestamp(), self.ping_delay_ms(), self.pong_delay_ms())
        task = self.order_tasks[task_id]
        self._websocket_place_order(task)

    def _rest_place_order(self, task:ApiTaskItem):
        params = dict()
        params['currency_pair'] = f'{task.base}_{task.quote}'.upper()
        params['side'] = task.order_side.lower()
        params['orderType'] = 'limit'
        params['force'] = 'gtc'
        params['price'] = str(task.price)
        params['amount'] = str(task.quantity)

        reply = self._request_rest('POST', '/api/v4/spot/orders', None, params, task.trigger_timestamp)
        reply.setProperty("task", task)
        reply.finished.connect(self._on_rest_order_replied)

    def _websocket_login(self):
        request = gen_websocket_spot_login(self._api_key, self._api_secret)
        self.send_websocket_message(request)

    def _read_websocket_login(self, json_data):
        data = json_data['data']
        if 'errs' in data:
            self.set_login(False)
            print('login errors:', data['errs']['message'])
        else:
            self.set_login(True)

    def _websocket_place_order(self, task:ApiTaskItem):
        request = gen_websocket_spot_order_place(task.task_id, task.base, task.quote, task.order_side, task.price, task.quantity, task.trigger_timestamp)
        self.send_websocket_message(request)

    def _read_websocket_order_ack(self, json_data):
        data = json_data['data']
        if 'ack' in json_data:
            self.traces[json_data['header']['trace_id']] = int(json_data['data']['result']['req_id'])
            return
        task_id = self.traces[json_data['header']['trace_id']]
        task = self.order_tasks[task_id]
        if json_data['header']['status'] == '200':
            task.mark_succeed()
            sql_order = self.gen_sql_order_task(task)
            self.order_task_updated.emit(sql_order)
        else:
            print('place_order errors:', data['errs']['message'])
            task.mark_failed()
            if task.is_outdated():
                sql_order = self.gen_sql_order_task(task)
                self.order_task_updated.emit(sql_order)
                return
            self.order_task_event(task.task_id)

    def _read_websocket_pong(self, json_data):
        ms = json_data['time_ms']
        self.mark_pong(ms, 0.5)
        print("Time:", get_timestamp(), self.server_timestamp(), self.time_offset, self.ping_delay_ms(), self.pong_delay_ms())

    def _read_websocket_balances(self, json_data):
        if json_data['event'] != 'update':
            return
        result = json_data['result'][0]
        currency = result['currency']
        balance = result['available']
        self.set_balance(currency, balance)

    def _read_websocket_orders(self, json_data):
        if json_data['event'] != 'update':
            return
        for order in json_data['result']:
            symbol = order['currency_pair'].split('_')
            sql_order = SqlOrder(
                order_id=int(order['id']),
                exchange='Gate.io',
                type=order['type'],
                side=order['side'],
                base=symbol[0],
                quote=symbol[1],
                price=order['price'],
                quantity=order['amount'],
                filled_quantity=order['filled_total'],
                avg_deal_price=order['avg_deal_price'],
                create_timestamp=int(order['create_time_ms']),
                status=order['finish_as']
            )
            if order['event'] == 'put':
                self.order_added.emit(sql_order)
            elif order['event'] == 'update':
                self.order_updated.emit(sql_order)
            elif order['event'] == 'finish' and sql_order.status == 'cancelled':
                self.order_removed.emit(sql_order)

    def _on_rest_time_replied(self):
        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()
        if reply.error() is not QNetworkReply.NetworkError.NoError:
            return
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        utc = json_data['server_time']
        self.mark_pong(utc)
        reply.deleteLater()

    def _get_initial_balance(self):
        reply = self._request_rest('GET', '/api/v4/spot/accounts', None, None, get_timestamp())
        reply.finished.connect(self._on_initial_balance_replied)

    def _get_initial_order(self):
        reply = self._request_rest('GET', '/api/v4/spot/open_orders', None, None, get_timestamp())
        reply.finished.connect(self._on_initial_order_replied)

    def _on_initial_balance_replied(self):
        reply = cast(QNetworkReply, self.sender())
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        balances = {item['currency']: float(item['available']) for item in json_data}
        self.set_balances(balances)

    def _on_initial_order_replied(self):
        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        for currency_pair in json_data:
            for order in currency_pair['orders']:
                symbol = order['currency_pair'].split('_')
                sql_order = SqlOrder(
                    order_id=int(order['id']),
                    exchange='Gate.io',
                    type=order['type'],
                    side=order['side'],
                    base=symbol[0],
                    quote=symbol[1],
                    price=order['price'],
                    quantity=order['amount'],
                    filled_quantity=order['filled_total'],
                    avg_deal_price='0',
                    create_timestamp=order['create_time_ms'],
                    status=order['status']
                )
                self.order_added.emit(sql_order)

    def _on_all_currencies_replied(self):
        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))

        def convert(pair: dict) -> SqlCurrency:
            base = pair['base']
            return SqlCurrency(
                exchange='Gate.io',
                base=base,
                quote=pair['quote'],
                exchange_logo='https://altcoinsbox.com/wp-content/uploads/2023/01/gate.io-logo.svg',
                base_logo=f'https://icon.gateimg.com/images/coin_icon/64/{base.lower()}.png',
                buy_timestamp=pair['buy_start'] * 1000,
                sell_timestamp=pair['sell_start'] * 1000,
                price_precision=pair['precision'],
                quantity_precision=pair['amount_precision']
            )

        pairs: list[SqlCurrency] = [convert(pair) for pair in json_data]
        self.currencies_updated.emit(pairs)

    @Slot(str)
    def cancel_order(self, order_id):
        order = self.database.get_order(self.exchange, int(order_id))

        params = dict()
        params['currency_pair'] = f'{order.base}_{order.quote}'.upper()

        self._request_rest('DELETE', f'/api/v4/spot/orders/{order_id}', params, None, get_timestamp())

    def _request_rest(self, method, api_path, query_params=None, body_params=None, minimum_timestamp=None):
        url = QUrl(API_URL + api_path)
        query = QUrlQuery()
        if query_params:
            for key, value in query_params.items():
                query.addQueryItem(key, value)
        url.setQuery(query)

        query_string = query.toString() if query_params else None
        body_string = json.dumps(body_params) if body_params else None

        timestamp = self.server_timestamp()
        if minimum_timestamp is not None:
            timestamp = max(timestamp, minimum_timestamp)

        # sign & header
        sign_headers = gen_signed_header(self._api_key, self._api_secret, method, api_path, int(timestamp / 1000),
                                         query_string, body_string)
        headers = HEADERS.copy()
        headers.update(sign_headers)

        request = QNetworkRequest(url)
        setup_header(headers, request)
        reply = None
        if method.upper() == 'GET':
            reply = self.http_manager.get(request)
        elif method.upper() == 'POST':
            reply = self.http_manager.post(request, body_string.encode())
        elif method.upper() == 'DELETE':
            reply = self.http_manager.deleteResource(request)
        return reply

    # deprecated
    @Slot()
    def _on_rest_order_replied(self):
        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()
        task = reply.property('task')
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = reply.readAll().data()
        json_data = json.loads(data)
        print(json_data)
        if status_code == 200 or status_code == 201:
            task.mark_succeed()
            sql_order = self.gen_sql_order_task(task)
            self.order_task_updated.emit(sql_order)
        else:
            qDebug(f'挂单失败: {json_data}')
            task.mark_failed()
            if task.is_outdated():
                sql_order = self.gen_sql_order_task(task)
                self.order_task_updated.emit(sql_order)
                return
            self.order_task_event(task.task_id)

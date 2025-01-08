import hashlib
import hmac
import json
import time
from typing import cast, Optional

from PySide6.QtCore import qDebug, Slot, QUrl, QUrlQuery
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtQml import QmlElement, QmlSingleton

from Python.API.ExchangeApi import ExchangeApiBase
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


def gen_websocket_sign(api_key, api_secret, channel, event='subscribe', payload=None):
    ts = int(time.time())
    sign_str = f'channel={channel}&event={event}&time={ts}'
    sign = hmac.new(api_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha512).hexdigest()
    request = {
        "time": ts,
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


def error_msg(status_code):
    msg = {
        202: '请求已被服务端接受，但是仍在处理中',
        204: '请求成功，服务端没有提供返回体',
        400: '无效请求',
        401: '认证失败',
        404: '未找到',
        429: '请求过于频繁'
    }
    return msg[status_code] if status_code in msg else '未知错误'


QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class GateApi(ExchangeApiBase):

    def __init__(self):
        super().__init__()
        self.exchange = "Gate.io"
        self.params = None
        self.open_websocket('wss://api.gateio.ws/ws/v4/')

    def connect_to_wallet(self):
        # balance
        self._get_initial_balance()
        request = gen_websocket_sign(self._api_key, self._api_secret, 'spot.balances', 'subscribe')
        self.send_websocket_message(request)
        # order
        self._get_initial_order()
        request = gen_websocket_sign(self._api_key, self._api_secret, 'spot.orders', 'subscribe', ['!all'])
        self.send_websocket_message(request)

    def websocket_connected_event(self):
        self.connect_to_wallet()

    def read_websocket_message(self, message: str):
        json_data = json.loads(message)
        channel = json_data['channel']
        if channel == 'spot.pong':
            return
        # balance
        if channel == 'spot.balances' and json_data['event'] == 'update':
            result = json_data['result'][0]
            currency = result['currency']
            balance = result['available']
            self.set_balance(currency, balance)
        # order
        elif channel == 'spot.orders':
            for order in json_data['result']:
                symbol = order['currency_pair'].split('_')
                sql_order = SqlOrder(
                    order_id=order['id'],
                    exchange='Gate.io',
                    type=order['type'],
                    side=order['side'],
                    base=symbol[0],
                    quote=symbol[1],
                    price=float(order['price']),
                    quantity=float(order['amount']),
                    filled_quantity=float(order['filled_total']),
                    avg_deal_price=float(order['avg_deal_price']),
                    create_timestamp=int(order['create_time_ms']),
                    status=order['finish_as']
                )
                if order['event'] == 'put':
                    self.order_added.emit(sql_order)
                elif order['event'] == 'update':
                    self.order_updated.emit(sql_order)
                elif order['event'] == 'finish' and sql_order.status == 'cancelled':
                    self.order_removed.emit(sql_order)

    def ping(self):
        request = QNetworkRequest(API_URL + SERVER_TIMESTAMP_URL)
        setup_header(HEADERS, request)
        self.mark_ping()
        reply = self.http_manager.get(request)
        reply.finished.connect(self._on_time_replied)

        # websocket_ping():
        ts = int(time.time())
        ping = {"time": ts, "channel": "spot.ping"}
        request = json.dumps(ping)
        self.send_websocket_message(request)

    def update_currencies(self):
        url = API_URL + SYMBOL_INFO_URL
        request = QNetworkRequest(url)
        setup_header(HEADERS, request)
        reply = self.http_manager.get(request)
        reply.finished.connect(self._on_all_currencies_replied)

    def _on_time_replied(self):
        reply = cast(QNetworkReply, self.sender())
        reply.deleteLater()
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        utc = json_data['server_time']
        self.mark_pong(utc)
        reply.deleteLater()

    def _get_initial_balance(self):
        reply = self._request('GET', '/api/v4/spot/accounts', {}, get_timestamp())
        reply.finished.connect(self._on_initial_balance_replied)

    def _get_initial_order(self):
        reply = self._request('GET', '/api/v4/spot/open_orders', {}, get_timestamp())
        reply.finished.connect(self._on_initial_order_replied)

    def _on_initial_balance_replied(self):
        reply = cast(QNetworkReply, self.sender())
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        balances = {item['currency']: item['available'] for item in json_data}
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
                    order_id=order['id'],
                    exchange='Gate.io',
                    type=order['type'],
                    side=order['side'],
                    base=symbol[0],
                    quote=symbol[1],
                    price=float(order['price']),
                    quantity=float(order['amount']),
                    filled_quantity=float(order['filled_total']),
                    avg_deal_price=0,
                    create_timestamp=int(order['create_time']) * 1000,
                    status=order['status']
                )
                self.order_added(sql_order)

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

    def order_task_2s_countdown_event(self, task_id):
        pass

    def order_task_event(self, task_id):
        task = self.order_tasks[task_id]

        params = dict()
        params['currency_pair'] = f'{task.base}_{task.quote}'.upper()
        params['side'] = task.order_side.lower()
        params['orderType'] = 'limit'
        params['force'] = 'gtc'
        params['price'] = task.price
        params['amount'] = task.quantity

        reply = self._request('POST', '/api/v4/spot/orders', params, task.trigger_timestamp)
        reply.setProperty("task", task)
        reply.finished.connect(self._on_order_replied)

    @Slot(int)
    def cancel_order(self, order_id):
        order = self.database.get_order(self.exchange, order_id)

        params = dict()
        params['currency_pair'] = f'{order.base}_{order.quote}'.upper()

        self._request('DELETE', f'/api/v4/spot/orders/{order_id}', params, get_timestamp())

    def _request(self, method, api_path, query_params=None, body_params=None, minimum_timestamp=None):
        url = QUrl(API_URL + api_path)
        query = QUrlQuery()
        if query_params is not None:
            for key, value in query_params.items():
                query.addQueryItem(key, value)
        url.setQuery(query)

        query_string = query.toString()
        body_string = json.dumps(body_params) if body_params is not None else None

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

    @Slot()
    def _on_order_replied(self):
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
            self.order_task_event(task.task_idx)

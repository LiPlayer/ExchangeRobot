import json
import time
from typing import cast
from PySide6.QtCore import qDebug, QObject, Slot
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtQml import QmlElement, QmlSingleton

import hashlib
import hmac

from Python.API.ExchangeApi import ExchangeApiBase, ApiTaskItem, gen_order_task
from Python.Constants import Currency
from Python.utils import setup_header, get_timestamp

# Base Url
API_URL = 'https://api.gateio.ws'
SERVER_TIMESTAMP_URL = '/api/v4/spot/time'
SYMBOL_INFO_URL = '/api/v4/spot/currency_pairs'
# http header
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}

def gen_signed_header(api_key, api_secret, timestamp_s, method, url, query_string=None, payload_string=None):
    sha = hashlib.sha512()
    sha.update((payload_string or "").encode('utf-8'))
    hashed_payload = sha.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, timestamp_s)
    sign = hmac.new(api_secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': api_key, 'Timestamp': str(timestamp_s), 'SIGN': sign}

def gen_websocket_sign(api_key, api_secret, channel, event='subscribe'):
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
        self.params = None
        self.open_websocket('wss://api.gateio.ws/ws/v4/')

    def connect_to_wallet(self):
        request = gen_websocket_sign(self._api_key, self._api_secret, 'spot.balances', 'subscribe')
        self.send_websocket_message(request)

    def websocket_connected_event(self):
        self.connect_to_wallet()

    def read_websocket_message(self, message:str):
        json_data = json.loads(message)
        channel = json_data['channel']
        if channel == 'spot.pong':
            return
        if channel == 'spot.balances' and json_data['event'] == 'update':
            result = json_data['result'][0]
            currency = result['currency']
            balance = result['available']
            self.set_balance(currency, balance)


    def websocket_ping(self):
        ts = int(time.time())
        ping = {"time": ts, "channel" : "spot.ping"}
        request = json.dumps(ping)
        self.send_websocket_message(request)

    def request_utctime(self):
        request = QNetworkRequest(API_URL + SERVER_TIMESTAMP_URL)
        setup_header(HEADERS, request)
        self.ping_time()
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_time_replied(reply))

    def request_all_currencies(self):
        url = API_URL + SYMBOL_INFO_URL
        request = QNetworkRequest(url)
        setup_header(HEADERS, request)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_all_currencies_replied(reply))

    def _on_time_replied(self, reply: QNetworkReply):
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        utc = json_data['server_time']
        self.pong_time(utc)
        reply.deleteLater()


    def _on_all_currencies_replied(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        def convert(pair: dict) -> Currency:
            base = pair['base']
            return Currency(
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

        pairs: list[Currency] = [convert(pair) for pair in json_data]
        self.currencies_updated.emit(pairs)


    def order_processing_2s_countdown_event(self, task_id):
        pass

    def order_processing_event(self, task_id):
        task = self.order_tasks[task_id]

        params = dict()
        params['currency_pair'] = f'{task.base}_{task.quote}'.upper()
        params['side'] = task.order_side.lower()
        params['orderType'] = 'limit'
        params['force'] = 'gtc'
        params['price'] = task.price
        params['amount'] = task.quantity

        reply = self._request('/api/v4/spot/orders', params, task.trigger_timestamp)
        reply.setProperty("task", task)
        reply.finished.connect(self._on_order_replied)

    def _request(self, api_path, params, minimum_timestamp=None):
        url = API_URL + api_path

        timestamp = self.rectified_timestamp()
        if minimum_timestamp is not None:
            timestamp = max(timestamp, minimum_timestamp)

        # sign & header
        body = json.dumps(params)
        sign_headers = gen_signed_header(self._api_key, self._api_secret, int(timestamp / 1000), 'POST', api_path, None, body)
        headers = HEADERS.copy()
        headers.update(sign_headers)

        request = QNetworkRequest(url)
        setup_header(headers, request)
        reply = self.http_manager.post(request, body.encode())
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
            sql_row = gen_order_task(task)
            self.order_task_updated.emit(sql_row)
        else:
            qDebug(f'挂单失败: {json_data}')
            task.mark_failed()
            if task.is_outdated():
                sql = gen_order_task(task)
                self.order_task_updated.emit(task)
                return
            self.order_processing_event(task.task_idx)

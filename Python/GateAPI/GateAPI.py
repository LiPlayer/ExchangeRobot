import json
from typing import cast
from PySide6.QtCore import qDebug
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from PySide6.QtQml import QmlElement, QmlSingleton

from Python.Constants import Currency
from Python.ExchangeApi import ExchangeApiBase
import hashlib
import hmac

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
class GateApiClient(ExchangeApiBase):
    def __init__(self):
        super().__init__()
        self.params = None

    def request_utctime(self):
        request = QNetworkRequest(API_URL + SERVER_TIMESTAMP_URL)
        setup_header(HEADERS, request)
        begin_ms = get_timestamp()
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_utc_replied(reply, begin_ms))

    def request_all_crypto_pairs(self):
        url = API_URL + SYMBOL_INFO_URL
        request = QNetworkRequest(url)
        setup_header(HEADERS, request)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_all_crypto_pairs_replied(reply))

    def _on_utc_replied(self, reply: QNetworkReply, begin_ms):
        end_ms = get_timestamp()
        delta_ms = (end_ms - begin_ms) // 2
        self.local_timestamp_base = end_ms

        # predict delay
        delay = int(0.4 * self.delay_ms + 0.6 * delta_ms)
        self._delay_ms = delay

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        utc = json_data['server_time']
        self.server_timestamp_base = utc + self.delay_ms
        reply.deleteLater()

        self.server_time_updated.emit()

    def _on_all_crypto_pairs_replied(self, reply: QNetworkReply):
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
                sell_timestamp=pair['sell_start'] * 1000
            )

        pairs: list[Currency] = [convert(pair) for pair in json_data]
        self.currencies_updated.emit(pairs)


    def order_trigger_5s_countdown_event(self):
        params = dict()
        params['currency_pair'] = (self.base + self.quote).upper()
        params['side'] = self.order_side
        params['orderType'] = 'limit'
        params['force'] = 'gtc'
        params['price'] = self.price
        params['amount'] = self.quantity
        self.params = params

    def order_start_event(self):
        super().order_start_event()
        minimum_timestamp = self.trigger_timestamp
        reply = self._request('/api/v4/spot/orders', self.params, minimum_timestamp)
        reply.finished.connect(self._on_order_replied)

    def _request(self, api_path, params, minimum_timestamp=None):
        url = API_URL + api_path

        timestamp = self.rectified_timestamp
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

    def _on_order_replied(self):
        reply = cast(QNetworkReply, self.sender())
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = reply.readAll().data()
        json_data = json.loads(data)
        if status_code == 200 or status_code == 201:
            self.order_finish_event()
        else:
            qDebug(f'挂单失败: {json_data}')
            if self.should_stop():
                self.order_finish_event()
            else:
                self.order_start_event()

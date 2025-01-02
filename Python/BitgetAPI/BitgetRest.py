import json
import re
import time
from typing import cast

from PySide6.QtCore import qDebug, Slot, QDateTime
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager
from bs4 import BeautifulSoup
from dateparser import parse

import Python.BitgetAPI.consts_bitget as const
import Python.BitgetAPI.utils_bitget as utils
from Python.utils import get_timestamp, setup_header
from Python.MiscSettings import BitgetConfiguration
from Python.RestClient import APIOrderBase, APIBase, SymbolInfo, CryptoPair


class BitgetCommon(APIBase):
    _delay_ms = 0
    server_timestamp_base = 0
    local_timestamp_base = 0

    def __init__(self):
        super().__init__()
        self._announcements = [{}]
        self._pairs = []

    @property
    def rectified_timestamp(self):
        timestamp = self.server_timestamp_base + (get_timestamp() - self.local_timestamp_base)
        return timestamp

    @property
    def delay_ms(self):
        return self._delay_ms

    def request_utctime(self):
        request = QNetworkRequest(const.API_URL + const.SERVER_TIMESTAMP_URL)
        begin_ms = get_timestamp()
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_utc_replied(reply, begin_ms))

    def request_symbol(self, symbol):
        url = const.API_URL + const.SYMBOL_INFO_URL + f'?symbol={symbol}'
        request = QNetworkRequest(url)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_symbol_info_replied(reply))

    # announcement first, then home quotation
    def request_all_crypto_pairs(self):
        url = (f'https://api.bitget.com/api/v2/public/annoucements?'
               f'language=en_US&annType=coin_listings')
        request = QNetworkRequest(url)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_announcement_replied(reply))

    def _on_utc_replied(self, reply: QNetworkReply, begin_ms):
        end_ms = get_timestamp()
        delta_ms = (end_ms - begin_ms) // 2
        self.local_timestamp_base = end_ms

        # predict delay
        delay = int(0.4 * self.delay_ms + 0.6 * delta_ms)
        self._delay_ms = delay

        data = reply.readAll().data()
        try:
            json_data = json.loads(data.decode('utf-8'))
        except:
            return
        utc = int(json_data['data']['serverTime'])
        self.server_timestamp_base = utc + self.delay_ms
        reply.deleteLater()

        self.server_time_updated.emit()

    def _on_symbol_info_replied(self, reply: QNetworkReply):
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        code = json_data['code']
        if code != '00000':
            if code == '40034':
                symbol = json_data['msg'].split()[1] # "Parameter xxx does not exist"
                self.symbol_info_not_existed.emit(symbol)
            return

        symbol_data = json_data['data'][0]
        symbol = symbol_data['symbol']
        price_precision = symbol_data['pricePrecision']
        quantity_precision = symbol_data['quantityPrecision']
        status = symbol_data['status']
        status_dict = {
            'offline': '维护',
            'gray': '灰度',
            'online': '上线',
            'halt': '停盘'
        }
        info = SymbolInfo(symbol, status_dict[status], price_precision, quantity_precision)
        self.symbol_info_updated.emit(info)

    def _on_home_quotation_replied(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        code = json_data['code']
        if code != '00000':
            return

        json_data = json_data['data']

        def convert(pair: dict) -> CryptoPair:
            base = pair['baseSymbol']
            return CryptoPair(
                exchange='Bitget',
                base=base,
                quote=pair['pricedSymbol'],
                exchange_logo='https://cryptologos.cc/logos/bitget-token-new-bgb-logo.svg',
                base_logo=pair['imgUrl'],
                buy_timestamp=pair['openTime'],
                sell_timestamp=pair['openTime']
            )

        pairs: list[CryptoPair] = [convert(pair) for pair in json_data]
        self.all_crypto_pairs_updated.emit(pairs)

    def _on_announcement_replied(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return
        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        code = json_data['code']
        if code != '00000':
            return
        self._pairs = []
        announcements = json_data['data']
        self._announcements = [item for item in announcements if 'Will List' in item['annTitle']]
        self._retrieve_listing_time_by_html(0)

    def _retrieve_listing_time_by_html(self, idx):
        url = self._announcements[idx]['annUrl']
        request = QNetworkRequest(url)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda i=idx: self._on_html_announcement_replied(reply, i))

    def _on_html_announcement_replied(self, reply: QNetworkReply, idx):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            self._retrieve_listing_time_by_html(idx + 1)
            return
        html_content = reply.readAll().data().decode('utf-8')
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        # 查找包含 "Trading Available:" 的 <p> 标签
        try:
            trading_text = soup.find('span', string= lambda x: x and "Trading Available" in x).parent.getText()
        except:
            return
        colon_idx = trading_text.find(':')
        time_str = trading_text[colon_idx+1:].strip()
        # 使用 dateparser 解析 UTC 时间
        parsed_time = parse(time_str)
        # 获取 Unix 时间戳
        unix_timestamp = int(parsed_time.timestamp()) * 1000

        soup = BeautifulSoup(html_content, 'html.parser')
        # 查找包含 "Spot Trading Link" 的 <span> 标签
        try:
            spot_trading_text = \
                soup.find('span', string=lambda x: x and "Spot Trading" in x).parent.find('a').find_all('span')[-1].text
        except:
            spot_trading_text = \
                soup.find('a', string=lambda x: x and "Spot Trading" in x).parent.parent.find_all('span')[-1].text
        symbol = spot_trading_text.strip().split('/')
        base = symbol[0]
        quote = symbol[1]
        pair = CryptoPair(
            exchange='Bitget',
            base=base,
            quote=quote,
            exchange_logo='https://cryptologos.cc/logos/bitget-token-new-bgb-logo.svg',
            base_logo='',
            buy_timestamp=unix_timestamp,
            sell_timestamp=unix_timestamp
        )

        self._pairs.append(pair)
        if idx == len(self._announcements) - 1:
            self.all_crypto_pairs_updated.emit(self._pairs)
            url = 'https://www.bitget.com/v1/mix/market/getHomeQuotation'
            request = QNetworkRequest(url)
            reply = self.http_manager.get(request)
            reply.finished.connect(lambda: self._on_home_quotation_replied(reply))
        else:
            self._retrieve_listing_time_by_html(idx + 1)


class BitgetOrder(APIOrderBase):
    common = BitgetCommon()

    def __init__(self, order_type: APIOrderBase.OrderType, symbol: str, price: str, quantity: str, interval=1,
                 trigger_timestamp=-1,
                 api_key=None, secret_key=None, passphrase=None):
        super().__init__(order_type, symbol, price, quantity, interval, trigger_timestamp)
        self.exchange = 'Bitget'

        config = BitgetConfiguration()
        self.API_KEY = api_key if api_key is not None else config.apikey()
        self.SECRET_KEY = secret_key if secret_key is not None else config.secretkey()
        self.PASSPHRASE = passphrase if passphrase is not None else config.passphrase()
        params = dict()
        params['symbol'] = self.symbol
        params['side'] = 'buy' if self.order_type == APIOrderBase.OrderType.Buy else 'sell'
        params['orderType'] = 'limit'
        params['force'] = 'gtc'
        params['price'] = self.price
        params['size'] = self.quantity
        self.params = params

        self.common.server_time_updated.connect(self.server_time_updated.emit)
        self.common.symbol_info_updated.connect(self.symbol_info_updated.emit)
        self.common.symbol_info_not_existed.connect(self.symbol_info_not_existed.emit)

    @property
    def rectified_timestamp(self):
        return self.common.rectified_timestamp

    @property
    def delay_ms(self):
        return self.common.delay_ms

    def request_utctime(self):
        self.common.request_utctime()

    def request_symbol(self, symbol):
        self.common.request_symbol(symbol)

    def request_all_crypto_pairs(self):
        self.common.request_all_crypto_pairs()

    def order_trigger_start_event(self):
        super().order_trigger_start_event()
        qDebug(f'开始执行下单: {str(self.params)}')

    def order_trigger_event(self):
        minimum_timestamp = self.trigger_timestamp
        reply = self._request('/api/v2/spot/trade/place-order', self.params, minimum_timestamp)
        reply.finished.connect(self._on_replied)

    def cancel_order(self):
        pass

    def _request(self, api_path, params, minimum_timestamp=None):
        url = const.API_URL + api_path

        timestamp = self.rectified_timestamp
        if minimum_timestamp is not None:
            timestamp = max(timestamp, minimum_timestamp)

        # sign & header
        body = json.dumps(params)
        sign = utils.sign(utils.pre_hash(timestamp, 'POST', api_path, str(body)), self.SECRET_KEY)
        headers = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE)

        request = QNetworkRequest(url)
        setup_header(headers, request)
        reply = self.http_manager.post(request, body.encode())
        return reply

    def _on_replied(self):
        reply = cast(QNetworkReply, self.sender())
        data = reply.readAll().data()
        json_data = json.loads(data)
        code = int(json_data['code'])
        if code == 00000:  # success
            order_id = json_data['data']['orderId']
            self.order_records.append(int(order_id))
            self.succeed_count += 1
            self.stop_order_trigger()
            if self.succeed_count == 1:
                qDebug(f'挂单成功，结束任务：{str(self.params)}')
            self.succeed.emit()
        else:  # error
            self.failed_count += 1
            if self.order_type == APIOrderBase.OrderType.Sell and code == 43012: # Insufficient balance
                qDebug(str(json_data))
            else:
                match code:
                    case 43009 | 40034 | 43012:
                        self.stop_order_trigger()
                        self.error_code = code
                        qDebug(f'挂单失败: {json_data}')
                        self.failed.emit()
                    case _:
                        if not self.is_finished():
                            qDebug(str(json_data))


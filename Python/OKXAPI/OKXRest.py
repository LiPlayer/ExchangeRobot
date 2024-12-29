import json

from PySide6.QtNetwork import QNetworkRequest, QNetworkReply

import Python.OKXAPI.consts_okx as const
from Python.RestClient import CryptoPair
from Python.RestClient import RestBase, SymbolInfo
from Python.utils import get_timestamp, setup_header


class OKXCommon(RestBase):
    _delay_ms = 0
    server_timestamp_base = 0
    local_timestamp_base = 0

    def __init__(self):
        super().__init__()

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
        setup_header(const.HEADERS, request)
        reply = self.http_manager.get(request)
        reply.finished.connect(lambda: self._on_symbol_info_replied(reply))

    def request_all_crypto_pairs(self):
        url = 'https://www.okx.com/api/v5/public/instruments?instType=SPOT'
        request = QNetworkRequest(url)
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
        try:
            json_data = json.loads(data.decode('utf-8'))
        except:
            return
        utc = json_data['serverTime']
        self.server_timestamp_base = utc + self.delay_ms
        reply.deleteLater()

        self.server_time_updated.emit()

    def _on_symbol_info_replied(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        json_data = json_data['symbols'][0]
        status = json_data['status']
        status_dict = {
            '1': '上架',
            '2': '暂停',
            '3': '下架'
        }
        info = SymbolInfo(json_data['symbol'], status_dict[status],
                          json_data['quotePrecision'], json_data['quoteAssetPrecision'])
        self.symbol_info_updated.emit(info)

    def _on_all_crypto_pairs_replied(self, reply: QNetworkReply):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            return

        data = reply.readAll().data()
        json_data = json.loads(data.decode('utf-8'))
        json_data = json_data['data']

        def convert(pair: dict) -> CryptoPair:
            open_time = 0
            return CryptoPair(
                exchange='OKX',
                base=pair['baseCcy'],
                quote=pair['quoteCcy'],
                exchange_logo='https://upload.wikimedia.org/wikipedia/commons/e/e4/OKX_Logo.svg',
                base_logo=f'https://www.okx.com/cdn/oksupport/asset/currency/icon/{pair['baseCcy'].lower()}.png',
                buy_timestamp=pair['listTime'],
                sell_timestamp=pair['listTime']
            )

        pairs: list[CryptoPair] = [convert(pair) for pair in json_data]
        self.all_crypto_pairs_updated.emit(pairs)

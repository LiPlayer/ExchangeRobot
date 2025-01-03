import json
from typing import cast

from PySide6.QtCore import qDebug, Slot
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager


from Python.RestClient import APIBase, SymbolInfo, APIOrderBase
from Python.utils import get_timestamp, setup_header
import Python.BinanceAPI.consts_binance as const

from Python.RestClient import CryptoPair


class BinanceCommon(APIBase):
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
        url = 'https://www.binance.com/bapi/apex/v1/public/apex/marketing/symbol/list'
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
            # qDebug(f'获取交易对出错：{error_msg(status_code)}')
            self.symbol_info_not_existed.emit('symbol')
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
            fields = ['planToOpenMarketTime', 'listingTime']
            open_time = next((pair[field] for field in fields if pair.get(field) is not None), 0)
            return CryptoPair(
                exchange='Binance',
                base=pair['baseAsset'],
                quote=pair['quoteAsset'],
                exchange_logo='https://upload.wikimedia.org/wikipedia/commons/1/12/Binance_logo.svg',
                base_logo=pair['logo'],
                buy_timestamp=open_time,
                sell_timestamp=open_time
            )

        pairs: list[CryptoPair] = [convert(pair) for pair in json_data]
        self.all_crypto_pairs_updated.emit(pairs)

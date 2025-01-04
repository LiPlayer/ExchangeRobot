from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, QTimer, QDateTime, Qt, Slot, Property
from PySide6.QtNetwork import QNetworkAccessManager

from Python.utils import get_timestamp

@dataclass
class SymbolInfo:
    symbol: str
    status: str
    price_precision: int
    quantity_precision: int

@dataclass
class CryptoPair:
    exchange: str
    base: str
    quote: str
    exchange_logo: str
    base_logo: str
    buy_timestamp: int
    sell_timestamp: int
    price_precision: int = 4
    quantity_precision: int = 4


class MetaQObjectABC(type(QObject), ABCMeta):
    pass


class ExchangeApiBase(QObject, metaclass=MetaQObjectABC):
    server_time_updated = Signal()
    currencies_updated = Signal(list)  # CryptoPair list
    state_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.try_idx = 0
        self.try_count = None
        self.quote = None
        self.base = None
        self._passphrase = None
        self._api_secret = None
        self._api_key = None
        self._state = None
        self.delay_ms = None
        self.server_timestamp_base = 0
        self.local_timestamp_base = 0
        self.http_manager = QNetworkAccessManager()

        self.trigger_check_timer = QTimer(self)  # in case of system time drifting
        self.trigger_timestamp = None
        self.quantity = None
        self.price = None
        self.order_side = None

    @Property(str)
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, key):
        self._api_key = key

    @Property(str)
    def api_secret(self):
        return self._api_secret

    @api_secret.setter
    def api_secret(self, key):
        self._api_secret = key

    @Property(str)
    def passphrase(self):
        return self._passphrase

    @passphrase.setter
    def passphrase(self, key):
        self._passphrase = key

    @property
    def rectified_timestamp(self):
        timestamp = self.server_timestamp_base + (get_timestamp() - self.local_timestamp_base)
        return timestamp

    def update_delay(self, ms):
        self.delay_ms = 0.5 * self.delay_ms + 0.5 * ms

    @abstractmethod
    def request_utctime(self):
        pass

    @abstractmethod
    def request_all_crypto_pairs(self):
        pass

    @Slot(str, str, str, str, str, int, int)
    def place_order(self, order_side: str, base: str, quote: str, price: str, quantity: str,
                    try_count=5, trigger_timestamp=-1):
        if self.try_idx > 0:
            print("place order failed: Don't call place_order twice for one instance.")
            return
        self.order_side = order_side
        self.base = base
        self.quote = quote
        self.price = price
        self.quantity = quantity
        self.trigger_timestamp = trigger_timestamp
        self.try_count = try_count

        self.trigger_check_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.trigger_check_timer.timeout.connect(self._on_check_time)
        self.trigger_check_timer.setSingleShot(True)

        server_time = self.rectified_timestamp
        if self.trigger_timestamp > 0:
            delta_ms = self.trigger_timestamp - server_time
            if delta_ms < 0:
                msg = (f'定时时间 {QDateTime.fromMSecsSinceEpoch(self.trigger_timestamp).toString()} '
                       f'不能晚于当前时间 {QDateTime.fromMSecsSinceEpoch(server_time).toString()}')
                return False, msg
            self._on_check_time()
        else:  # start immediately
            self.trigger_timestamp = server_time
            self.order_start_event()
        return True, 'success'

    # @abstractmethod
    # def cancel_order(self):
    #     pass

    def order_trigger_5s_countdown_event(self):
        pass

    @abstractmethod
    def order_start_event(self):
        self.try_idx += 1

    def order_finish_event(self):
        if self.try_idx < self.try_count:
            self.state = "Succeed"
        else:
            self.state = "Failed"

    def should_stop(self):
        return self.try_idx >= self.try_count

    @Property(str, notify=state_changed)
    def state(self):
        return self._state

    @state.setter
    def state(self, st):
        if self._state != st:
            self._state = st
            self.state_changed.emit(st)

    def countdown_ms(self):
        ms = self.trigger_timestamp - self.rectified_timestamp - self.delay_ms
        return ms

    def _on_check_time(self):
        delta_ms = self.countdown_ms()
        if delta_ms < 1000:  # trigger
            self.order_start_event()
        elif delta_ms < 5000:  # 5s
            self.trigger_check_timer.setInterval(delta_ms)
            self.trigger_check_timer.start()
            self.order_trigger_5s_countdown_event()
        else:  # > 5s
            check_time = delta_ms - 5000
            self.trigger_check_timer.setInterval(check_time)
            self.trigger_check_timer.start()

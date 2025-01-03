from abc import abstractmethod, ABCMeta
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, QTimer, QDateTime, Qt
from PySide6.QtNetwork import QNetworkAccessManager


class MetaQObjectABC(type(QObject), ABCMeta):
    pass

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


class APIBase(QObject, metaclass=MetaQObjectABC):
    server_time_updated = Signal()
    symbol_info_updated = Signal(SymbolInfo)
    symbol_info_not_existed = Signal(str)
    all_crypto_pairs_updated = Signal(list)  # CryptoPair list
    http_manager = QNetworkAccessManager()

    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def rectified_timestamp(self):
        pass
    
    @property
    @abstractmethod
    def delay_ms(self):
        pass

    @abstractmethod
    def request_utctime(self):
        pass

    @abstractmethod
    def request_symbol(self, symbol):
        pass

    @abstractmethod
    def request_all_crypto_pairs(self):
        pass

class APIOrderBase(APIBase):
    succeed = Signal()
    failed = Signal()

    class OrderType(Enum):
        Buy = 1
        Sell = 2

    def __init__(self, order_type:OrderType, symbol:str, price:str, quantity:str, interval = 1, trigger_timestamp=-1):
        super().__init__()
        self.exchange = ''
        self.order_type = order_type
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.interval = interval
        self.trigger_timestamp = trigger_timestamp
        self.order_records = []
        self.succeed_count = 0
        self.failed_count = 0
        self.error_code = -1 # fatal error, means no need to do more requesting

        self.trigger_timer = QTimer(self)
        self.trigger_timer.setInterval(interval)
        self.trigger_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.trigger_timer.timeout.connect(self.order_trigger_event)
        self.trigger_check_timer = QTimer(self)  # in case of system time drifting
        self.trigger_check_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.trigger_check_timer.timeout.connect(self._on_check_time)
        self.trigger_check_timer.setSingleShot(True)

    def place_order(self):
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
            self.order_trigger_start_event()
        return True, 'success'

    @abstractmethod
    def cancel_order(self):
        pass

    def stop_order_trigger(self):
        self.trigger_timer.stop()

    def order_trigger_5s_countdown_event(self):
        pass

    def order_trigger_start_event(self):
        self.order_trigger_event()
        self.trigger_timer.start()

    @abstractmethod
    def order_trigger_event(self):
        pass

    def is_running(self):
        return self.is_trigger_active()

    def is_finished(self):
        return (self.succeed_count + self.failed_count) > 0 and not self.is_trigger_active()

    def has_error(self):
        return self.error_code > 0

    def is_trigger_active(self):
        return self.trigger_timer.isActive()

    def countdown_ms(self):
        ms = self.trigger_timestamp - self.rectified_timestamp - self.delay_ms
        return ms

    def _on_check_time(self):
        delta_ms = self.countdown_ms()
        if delta_ms < 1000:    # trigger
            self.order_trigger_start_event()
        elif delta_ms < 5000:   # 5s
            self.trigger_check_timer.setInterval(delta_ms)
            self.trigger_check_timer.start()
            self.order_trigger_5s_countdown_event()
        else:   # > 5s
            check_time = delta_ms - 5000
            self.trigger_check_timer.setInterval(check_time)
            self.trigger_check_timer.start()

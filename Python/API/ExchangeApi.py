from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, QTimer, Qt, Slot, Property
from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtWebSockets import QWebSocket

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

class TaskItem(QObject):
    countdown_2s = Signal(int)
    requested = Signal(int)

    def __init__(self, task_idx: int, order_side: str, base: str, quote: str, price: str, quantity: str,
                    try_count=5, trigger_timestamp=-1):
        super().__init__()
        self.task_idx = task_idx
        self.order_side = order_side
        self.base = base
        self.quote = quote
        self.price = price
        self.quantity = quantity
        self.trigger_timestamp = trigger_timestamp
        self.state = "Idle"

        self.rectified_time = None
        self.delay_time = None

        self.try_idx = 0
        self.try_count = try_count

        self.valid = False

        self.timer = QTimer(self)  # in case of system time drifting
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_check_time)
        self.timer.setSingleShot(True)

    def set_time_hook(self, rectified_time, delay_time):
        self.rectified_time = rectified_time
        self.delay_time = delay_time

    def start(self):
        server_time = self.rectified_time()
        self.trigger_timestamp = max(self.trigger_timestamp, server_time)

        if self.trigger_timestamp == server_time:   # start immediately
            self.trigger_timestamp = server_time
            self._start_request()
        else:   # timer trigger
            self._on_check_time()

    def mark_succeed(self):
        self.try_idx += 1
        self.state = "Succeed"

    def mark_failed(self):
        self.try_idx += 1
        self.state = "Failed"

    def is_outdated(self):
        return self.try_idx >= self.try_count

    def _countdown_ms(self):
        ms = self.trigger_timestamp - self.rectified_time - self.delay_time()
        return ms

    def _start_request(self):
        if self.try_idx == 0:
            self.state = "Started"
        self.requested.emit(self.task_idx)

    def _on_check_time(self):
        delta_ms = self._countdown_ms()
        if delta_ms < 1000:  # trigger
            self._start_request()
        elif delta_ms < 2000:  # 2s
            self.timer.setInterval(delta_ms)
            self.timer.start()
            self.countdown_2s.emit(self.task_idx)
        else:  # > 2s
            check_time = delta_ms - 2000
            self.timer.setInterval(check_time)
            self.timer.start()

class ExchangeApiBase(QObject, metaclass=MetaQObjectABC):
    server_time_updated = Signal()
    currencies_updated = Signal(list)  # Currency list
    balances_updated = Signal()

    api_key_changed = Signal(str)
    api_secret_changed = Signal(str)
    passphrase_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._ping_time = None

        self._passphrase = None
        self._api_secret = None
        self._api_key = None
        self.delay_ms = 0
        self.server_timestamp_base = 0
        self.local_timestamp_base = 0

        self.http_manager = QNetworkAccessManager()
        self.websocket = QWebSocket()
        self.websocket.textMessageReceived.connect(self.read_websocket_message)
        self.websocket.connected.connect(self.websocket_connected_event)
        self.websocket.disconnected.connect(self.websocket_disconnected_event)
        self.websocket.connected.connect(lambda : print("connected"))
        self.websocket.disconnected.connect(lambda : print("disconnected"))

        self.websocket_timer = QTimer(self)
        self.websocket_timer.setSingleShot(False)
        self.websocket_timer.setInterval(5000)
        self.websocket_timer.timeout.connect(self.websocket_ping)
        self.websocket_timer.start()

        self.rest_timer = QTimer(self)
        self.rest_timer.setSingleShot(False)
        self.rest_timer.setInterval(1000)
        self.rest_timer.timeout.connect(self.request_utctime)
        self.rest_timer.start()

        self.balances = {}
        self.order_tasks: dict[int, TaskItem] = {}

    def open_websocket(self, url):
        self.websocket.open(url)

    @Slot()
    def websocket_connected_event(self):
        pass

    @Slot()
    def websocket_disconnected_event(self):
        pass

    @Slot(str)
    def read_websocket_message(self, message:str):
        pass

    def send_websocket_message(self, message:str):
        self.websocket.sendTextMessage(message)

    @abstractmethod
    def websocket_ping(self):
        pass

    @abstractmethod
    @Slot()
    def connect_to_wallet(self):
        pass

    @Slot(str, result=str)
    def balance(self, currency):
        return self.balances.get(currency, '0')

    def set_balance(self, currency, bal):
        self.balances.update({currency : bal})
        self.balances_updated.emit()

    @property
    def delay_millisecond(self):
        return self.delay_ms

    @Property(str, notify=api_key_changed)
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, key):
        self._api_key = key

    @Property(str, notify=api_secret_changed)
    def api_secret(self):
        return self._api_secret

    @api_secret.setter
    def api_secret(self, key):
        self._api_secret = key

    @Property(str, notify=passphrase_changed)
    def passphrase(self):
        return self._passphrase

    @passphrase.setter
    def passphrase(self, key):
        self._passphrase = key

    # @Property(int, notify=server_time_updated)
    def rectified_timestamp(self):
        timestamp = self.server_timestamp_base + (get_timestamp() - self.local_timestamp_base)
        return timestamp

    def ping_time(self):
        self._ping_time = get_timestamp()

    def pong_time(self, server_time):
        end_ms = get_timestamp()
        delta_ms = (end_ms - self._ping_time) // 2

        # predict delay
        self.delay_ms = int(0.4 * self.delay_ms + 0.6 * delta_ms)

        self.local_timestamp_base = end_ms
        self.server_timestamp_base = server_time + self.delay_ms
        self.server_time_updated.emit()


    @abstractmethod
    def request_utctime(self):
        pass

    @abstractmethod
    def request_all_currencies(self):
        pass

    @Slot(str, str, str, str, str, int, int)
    def place_order(self, order_side: str, base: str, quote: str, price: str, quantity: str,
                    trigger_timestamp=-1, try_count=5):
        idx = len(self.order_tasks)
        task = TaskItem(idx, order_side, base, quote, price, quantity, try_count, trigger_timestamp)
        task.set_time_hook(self.rectified_timestamp, self.delay_millisecond)
        task.countdown_2s.connect(self.order_processing_2s_countdown_event)
        task.requested.connect(self.order_processing_event)
        self.order_tasks[idx] = task
        task.start()

    # @abstractmethod
    # def cancel_order(self):
    #     pass

    @Slot(int)
    def order_processing_2s_countdown_event(self, task_id):
        pass

    @abstractmethod
    @Slot(int)
    def order_processing_event(self, task_id):
        pass


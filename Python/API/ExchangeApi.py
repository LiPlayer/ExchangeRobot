from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, Signal, QTimer, Qt, Slot, Property
from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtWebSockets import QWebSocket

from Python.Constants import SqlOrderTask, SqlOrder
from Python.Database import  Database
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

class ApiTaskItem(QObject):
    countdown_2s = Signal(int)
    requested = Signal(int)

    def __init__(self, task_idx: int, order_side: str, base: str, quote: str, price: float, quantity: float,
                    trigger_timestamp=-1):
        super().__init__()
        self.task_idx = task_idx
        self.order_side = order_side
        self.base = base
        self.quote = quote
        self.price = price
        self.quantity = quantity
        self.trigger_timestamp = trigger_timestamp
        self.status = "Pending"

        self.server_time = None
        self.ping_delay = None
        self.custom_delay = None

        self.try_idx = 0
        self.try_count = 5

        self.valid = False

        self.timer = QTimer(self)  # in case of system time drifting
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_check_time)
        self.timer.setSingleShot(True)

    def set_time_delay_hook(self, server_time, ping_delay, custom_delay):
        self.server_time = server_time
        self.ping_delay = ping_delay
        self.custom_delay = custom_delay

    def start(self):
        server_time = self.server_time()
        self.trigger_timestamp = max(self.trigger_timestamp, server_time)

        if self.trigger_timestamp == server_time:   # start immediately
            self.trigger_timestamp = server_time
            self._start_request()
        else:   # timer trigger
            self._on_check_time()

    def mark_succeed(self):
        self.try_idx += 1
        self.status = "Succeed"

    def mark_failed(self):
        self.try_idx += 1
        self.status = "Failed"

    def is_outdated(self):
        return self.try_idx >= self.try_count

    def _countdown_ms(self):
        ms = self.trigger_timestamp - self.server_time() - self.ping_delay() - self.custom_delay()
        return ms

    def _start_request(self):
        if self.try_idx == 0:
            self.status = "Started"
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

    order_added = Signal(SqlOrder)
    order_updated = Signal(SqlOrder)
    order_removed = Signal(SqlOrder)

    order_task_added = Signal(SqlOrderTask)
    order_task_updated = Signal(SqlOrderTask)
    order_task_removed = Signal(SqlOrderTask)

    api_key_changed = Signal(str)
    api_secret_changed = Signal(str)
    passphrase_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.time_offset = 0
        self.pong_delay = 0
        self.ping_delay = 0
        self._custom_delay = 0
        self._ping_local_time = None
        self.exchange = ''
        self.database:Optional[Database] = None

        self._passphrase = None
        self._api_secret = None
        self._api_key = None

        self.http_manager = QNetworkAccessManager()
        self.websocket = QWebSocket()
        self.websocket.textMessageReceived.connect(self.read_websocket_message)
        self.websocket.connected.connect(self.websocket_connected_event)
        self.websocket.disconnected.connect(self.websocket_disconnected_event)
        self.websocket.connected.connect(lambda : print("connected"))
        self.websocket.disconnected.connect(lambda : print("disconnected"))

        self.ping_timer = QTimer(self)
        self.ping_timer.setSingleShot(False)
        self.ping_timer.setInterval(1000)
        self.ping_timer.timeout.connect(self.ping)
        self.ping_timer.start()

        self.balances = {}
        self.order_tasks: dict[int, ApiTaskItem] = {}

    @Property(Database)
    def db(self):
        return self.database

    @db.setter
    def db(self, db: Database):
        self.database = db
        self.recover_order_task()
        self.currencies_updated.connect(self.database.update_currencies)

        self.order_added.connect(self.database.add_order)
        self.order_updated.connect(self.database.update_order)
        self.order_removed.connect(self.database.remove_order)

        self.order_task_added.connect(self.database.add_order_task)
        self.order_task_updated.connect(self.database.update_order_task)
        self.order_task_removed.connect(self.database.remove_order_task)

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
    @Slot()
    def connect_to_wallet(self):
        pass

    @Slot(str, result=float)
    def balance(self, currency):
        return self.balances.get(currency, 0)

    def set_balance(self, currency:str, bal:float):
        self.balances.update({currency : bal})
        self.balances_updated.emit()

    def set_balances(self, balances:dict[str, float]):
        self.balances.update(balances)
        self.balances_updated.emit()

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

    def ping_delay_ms(self):
        return self.ping_delay

    def pong_delay_ms(self):
        return self.pong_delay

    def pingpong_delay(self):
        return self.ping_delay + self.pong_delay

    def set_custom_delay(self, delay_ms):
        self._custom_delay = delay_ms

    def custom_delay(self):
        return self._custom_delay

    # @Property(int, notify=server_time_updated)
    def server_timestamp(self):
        timestamp = get_timestamp() + self.time_offset
        return timestamp

    def mark_ping(self):
        self._ping_local_time = get_timestamp()

    def mark_pong(self, server_time, factor=0.5):
        local_time = get_timestamp()
        delta_ms = local_time - self._ping_local_time
        old_delay = self.pingpong_delay()

        # rectified delay
        delay_ms = int(0.8 * old_delay + 0.2 * delta_ms)
        self.ping_delay = int(delay_ms * factor)
        self.pong_delay = delay_ms - self.ping_delay
        time_offset = server_time + self.pong_delay - local_time
        self.time_offset = int(0.9 * self.time_offset + 0.1 * time_offset)

        self.server_time_updated.emit()

    @abstractmethod
    def ping(self):
        pass

    @abstractmethod
    @Slot()
    def update_currencies(self):
        pass

    def recover_order_task(self):
        if len(self.order_tasks) != 0:
            print('Warning: recover_order_task called but there are already some tasks')
            return
        cur_timestamp = self.server_timestamp()
        tasks = self.database.get_order_task(self.exchange)
        for item in tasks:
            task = self._create_order_task(item.task_id, item.side, item.base, item.quote, item.price,
                                           item.quantity, item.timestamp)
            if task.trigger_timestamp > cur_timestamp:
                task.start()
            self.order_tasks[task.task_idx] = task

    @Slot(str, str, str, float, float, float)
    def place_order_task(self, order_side: str, base: str, quote: str, price: float, quantity: float,
                         trigger_timestamp:float):
        task_id = 0 if len(self.order_tasks) == 0 else max(self.order_tasks)+1
        task = self._create_order_task(task_id, order_side, base, quote, price, quantity, int(trigger_timestamp))
        task.start()
        self.order_tasks[task_id] = task

        # notify
        sql_row = self.gen_sql_order_task(task)
        self.order_task_added.emit(sql_row)

    @Slot(int)
    def cancel_order_task(self, task_id):
        task = self.order_tasks.pop(task_id, None)
        if task is None:
            return
        task.deleteLater()

        # notify
        sql_row = self.gen_sql_order_task(task)
        self.order_task_removed.emit(sql_row)

    @Slot(int)
    def cancel_order(self, order_id):
        pass

    def _create_order_task(self, task_id, order_side: str, base: str, quote: str, price: float, quantity: float,
                           trigger_timestamp:int):
        task = ApiTaskItem(task_id, order_side, base, quote, price, quantity, trigger_timestamp)
        task.set_time_delay_hook(self.server_timestamp, self.ping_delay_ms, self.custom_delay)
        task.countdown_2s.connect(self.order_task_2s_countdown_event)
        task.requested.connect(self.order_task_event)
        return task

    def gen_sql_order_task(self, task: ApiTaskItem):
        order = SqlOrderTask(
            task_id=task.task_idx,
            exchange=self.exchange,
            side=task.order_side,
            type='limit',
            base=task.base,
            quote=task.quote,
            price=float(task.price),
            quantity=float(task.quantity),
            timestamp=task.trigger_timestamp,
            status=task.status
        )
        return order

    # @abstractmethod
    # def cancel_order(self):
    #     pass

    @Slot(int)
    def order_task_2s_countdown_event(self, task_id):
        pass

    @abstractmethod
    @Slot(int)
    def order_task_event(self, task_id):
        pass


from dataclasses import dataclass
from decimal import Decimal

from PySide6.QtCore import Qt

DatabaseName = 'Database.db'

CurrencyTable = 'CurrencyTable'
CurrencyFields = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
    ("exchange", "TEXT NOT NULL"),
    ("base", "TEXT NOT NULL"),
    ("quote", "TEXT NOT NULL"),
    ("exchange_logo", "TEXT"),
    ("base_logo", "TEXT"),
    ("buy_timestamp", "INTEGER"),
    ("sell_timestamp", "INTEGER"),
    ("price_precision", "INTEGER"),
    ("quantity_precision", "INTEGER"),
    ("favorite", "BOOLEAN"),
    ("is_new", "BOOLEAN")
]

@dataclass
class SqlCurrency:
    exchange: str
    base: str
    quote: str
    exchange_logo: str
    base_logo: str
    buy_timestamp: int
    sell_timestamp: int
    price_precision: int = 4
    quantity_precision: int = 4


OrderTaskTable = 'OrderTaskTable'
OrderTaskFields = [
    ("task_id", "INTEGER NOT NULL"),
    ("exchange", "TEXT NOT NULL"),
    ("type", "TEXT"),
    ("side", "TEXT"),
    ("base", "TEXT"),
    ("quote", "TEXT"),
    ("price", "TEXT"),
    ("quantity", "TEXT"),
    ("timestamp", "INTEGER"),
    ("status", "TEXT"),
]

@dataclass
class SqlOrderTask:
    task_id: int
    exchange: str
    type: str
    side: str
    base: str
    quote: str
    price: str
    quantity: str
    timestamp: int
    status: str


OrderTable = 'OrderTable'
OrderFields = [
    ("order_id", "INTEGER NOT NULL"),
    ("exchange", "TEXT NOT NULL"),
    ("type", "TEXT"),
    ("side", "TEXT"),
    ("base", "TEXT"),
    ("quote", "TEXT"),
    ("price", "TEXT"),
    ("quantity", "TEXT"),
    ("filled_quantity", "TEXT"),
    ("avg_deal_price", "TEXT"),
    ("create_timestamp", "INTEGER"),
    ("status", "TEXT"),
]


@dataclass
class SqlOrder:
    order_id: int
    exchange: str
    type: str
    side: str
    base: str
    quote: str
    price: str
    quantity: str
    filled_quantity: str
    avg_deal_price: str
    create_timestamp: int
    status: str


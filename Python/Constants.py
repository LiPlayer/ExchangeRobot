from dataclasses import dataclass
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
class Currency:
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
    ("side", "TEXT"),
    ("type", "TEXT"),
    ("base", "TEXT"),
    ("quote", "TEXT"),
    ("price", "REAL"),
    ("quantity", "REAL"),
    ("timestamp", "INTEGER"),
    ("state", "TEXT"),
]

@dataclass
class OrderTask:
    task_id: int
    exchange: str
    type: str
    side: str
    base: str
    quote: str
    price: float
    quantity: float
    timestamp: int
    state: str
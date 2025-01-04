from dataclasses import dataclass
from PySide6.QtCore import Qt

DatabaseName = 'Database.db'
CurrencyTable = 'CurrencyTable'
class CurrencyRole:
    IDRole = Qt.ItemDataRole.UserRole + 1
    ExchangeRole = Qt.ItemDataRole.UserRole + 2
    BaseRole = Qt.ItemDataRole.UserRole + 3
    QuoteRole = Qt.ItemDataRole.UserRole + 4
    ExchangeLogoRole = Qt.ItemDataRole.UserRole + 5
    BaseLogoRole = Qt.ItemDataRole.UserRole + 6
    BuyTimeRole = Qt.ItemDataRole.UserRole + 7
    SellTimeRole = Qt.ItemDataRole.UserRole + 8
    FavoriteRole = Qt.ItemDataRole.UserRole + 9
    IsNewRole = Qt.ItemDataRole.UserRole + 10

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
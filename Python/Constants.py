from dataclasses import dataclass
from PySide6.QtCore import Qt

DatabaseName = 'Database.db'
CurrencyTable = 'CurrencyTable'
class CurrencyField:
    IDRole = Qt.ItemDataRole.UserRole + 1
    ExchangeRole = Qt.ItemDataRole.UserRole + 2
    BaseRole = Qt.ItemDataRole.UserRole + 3
    QuoteRole = Qt.ItemDataRole.UserRole + 4
    ExchangeLogoRole = Qt.ItemDataRole.UserRole + 5
    BaseLogoRole = Qt.ItemDataRole.UserRole + 6
    BuyTimeRole = Qt.ItemDataRole.UserRole + 7
    SellTimeRole = Qt.ItemDataRole.UserRole + 8
    FavoriteRole = Qt.ItemDataRole.UserRole + 9


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
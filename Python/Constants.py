from enum import Enum

from PySide6.QtCore import Qt

CryptoPairsTable = 'CryptoPairs'
class CryptoPairsField:
    IDRole = Qt.ItemDataRole.UserRole + 1
    ExchangeRole = Qt.ItemDataRole.UserRole + 2
    BaseRole = Qt.ItemDataRole.UserRole + 3
    QuoteRole = Qt.ItemDataRole.UserRole + 4
    ExchangeLogoRole = Qt.ItemDataRole.UserRole + 5
    BaseLogoRole = Qt.ItemDataRole.UserRole + 6
    BuyTimeRole = Qt.ItemDataRole.UserRole + 7
    SellTimeRole = Qt.ItemDataRole.UserRole + 8
    FavoriteRole = Qt.ItemDataRole.UserRole + 9

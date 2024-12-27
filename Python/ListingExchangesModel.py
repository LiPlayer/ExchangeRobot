from PySide6.QtCore import Qt, Slot
from PySide6.QtSql import QSqlQueryModel, QSqlQuery

from Python.CryptoDatabase import CryptoDatabase
from Python.CryptoDatabase import CryptoDatabase as DB
from Python.utils import get_timestamp


class ListingExchangeModel(QSqlQueryModel):
    def __init__(self, db: CryptoDatabase):
        super().__init__(db)
        _db = db
        self._crypto = '-'
        self.setHeaderData(0, Qt.Orientation.Horizontal, 'exchange')
        self.setHeaderData(1, Qt.Orientation.Horizontal, 'exchange_logo')
        self.setHeaderData(2, Qt.Orientation.Horizontal, 'base')
        self.setHeaderData(3, Qt.Orientation.Horizontal, 'buy_timestamp')

        _db.data_updated.connect(self._on_updated)

    @Slot(str)
    def setCrypto(self, crypto):
        self._crypto = crypto
        self._on_updated()

    def _on_updated(self):
        state = (f'SELECT base, exchange, exchange_logo, buy_timestamp '
                 f'FROM {CryptoDatabase.CryptoPairsTB} '
                 f'WHERE base = \'{self._crypto}\' '
                 f'ORDER BY buy_timestamp ASC;')
        self.setQuery(state)

    def roleNames(self):
        roles = {
            DB.BaseRole : b'base',
            DB.ExchangeRole: b'exchange',
            DB.ExchangeLogoRole: b'exchange_logo',
            DB.BuyTimeRole: b'buy_timestamp'
        }
        return roles

    def data(self, item, role = ...):
        match role:
            case DB.BaseRole:
                ret = super().data(item)
            case DB.ExchangeRole:
                ret = super().data(item.siblingAtColumn(1))
            case DB.ExchangeLogoRole:
                ret = super().data(item.siblingAtColumn(2))
            case DB.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(3))
            case _:
                ret = super().data(item)
        return ret
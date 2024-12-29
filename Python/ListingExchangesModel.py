from PySide6.QtCore import Qt, Slot
from PySide6.QtSql import QSqlQueryModel, QSqlQuery

from Python.Database import Database
from Python.Database import Database as DB
from Python.utils import get_timestamp


class ListingExchangeModel(QSqlQueryModel):
    def __init__(self, db: Database):
        super().__init__(db)
        _db = db
        self._crypto = '-'

        self.setHeaderData(0, Qt.Orientation.Horizontal, 'id')
        self.setHeaderData(1, Qt.Orientation.Horizontal, 'exchange')
        self.setHeaderData(2, Qt.Orientation.Horizontal, 'exchange_logo')
        self.setHeaderData(3, Qt.Orientation.Horizontal, 'base')
        self.setHeaderData(4, Qt.Orientation.Horizontal, 'base_logo')
        self.setHeaderData(5, Qt.Orientation.Horizontal, 'buy_timestamp')
        self.setHeaderData(6, Qt.Orientation.Horizontal, 'favorite')

        _db.data_updated.connect(self._on_updated)

    @Slot(str)
    def setCrypto(self, crypto):
        self._crypto = crypto
        self._on_updated()

    def _on_updated(self):
        state = (f'SELECT id, exchange, exchange_logo, base, base_logo, buy_timestamp, favorite '
                 f'FROM {Database.CryptoPairsTB} '
                 f'WHERE base = \'{self._crypto}\' '
                 f'ORDER BY buy_timestamp ASC;')
        self.setQuery(state)

    def roleNames(self):
        roles = {
            DB.IDRole: b'id',
            DB.ExchangeRole: b'exchange',
            DB.ExchangeLogoRole: b'exchange_logo',
            DB.BaseRole : b'base',
            DB.BaseLogoRole: b'base_logo',
            DB.BuyTimeRole: b'buy_timestamp',
            DB.FavoriteRole: b'favorite'
        }
        return roles

    def data(self, item, role = ...):
        match role:
            case DB.IDRole:
                ret = super().data(item.siblingAtColumn(0))
            case DB.ExchangeRole:
                ret = super().data(item.siblingAtColumn(1))
            case DB.ExchangeLogoRole:
                ret = super().data(item.siblingAtColumn(2))
            case DB.BaseRole:
                ret = super().data(item.siblingAtColumn(3))
            case DB.BaseLogoRole:
                ret = super().data(item.siblingAtColumn(4))
            case DB.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(5))
            case DB.FavoriteRole:
                ret = super().data(item.siblingAtColumn(6))
            case _:
                ret = super().data(item)
        return ret

    def setData(self, index, value, role=...):
        match role:
            case DB.ExchangeRole:
                field = 'exchange'
            case DB.ExchangeLogoRole:
                field = 'exchange_logo'
            case DB.BaseRole:
                field = 'base'
            case DB.BaseLogoRole:
                field = 'base_logo'
            case DB.BuyTimeRole:
                field = 'buy_time'
            case DB.FavoriteRole:
                field = 'favorite'
            case _:
                field = 'favorite'
        _id = self.data(index.siblingAtColumn(0))
        state = f'UPDATE {Database.CryptoPairsTB} SET {field} = {value} WHERE id = {_id};'
        query = QSqlQuery(state)
        ok = query.exec()
        self._on_updated()
        self.dataChanged.emit(index, index)
        return ok
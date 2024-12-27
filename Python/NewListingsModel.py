import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug, Qt
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlQuery
from PySide6.QtWidgets import QTableView

from Python.CryptoDatabase import CryptoDatabase
from Python.CryptoDatabase import CryptoDatabase as DB
from Python.utils import get_timestamp


class NewListingsModel(QSqlQueryModel):
    def __init__(self, db: CryptoDatabase):
        super().__init__(db)
        _db = db
        self.setHeaderData(0, Qt.Orientation.Horizontal, 'base')
        self.setHeaderData(1, Qt.Orientation.Horizontal, 'base_logo')
        self.setHeaderData(2, Qt.Orientation.Horizontal, 'buy_timestamp')
        self.setHeaderData(3, Qt.Orientation.Horizontal, 'favorite')

        _db.data_updated.connect(self._on_updated)


    def _on_updated(self):
        now = get_timestamp()
        state = (f'SELECT base, base_logo, MAX(buy_timestamp) AS timestamp, favorite '
                 f'FROM {CryptoDatabase.CryptoPairsTB} '
                 f'WHERE buy_timestamp > {now} '
                 f'GROUP BY base '
                 f'ORDER BY timestamp ASC;')
        self.setQuery(state)

    def roleNames(self):
        roles = {
            DB.BaseRole : b'base',
            DB.BaseLogoRole: b'base_logo',
            DB.BuyTimeRole: b'buy_timestamp',
            DB.FavoriteRole: b'favorite'
        }
        return roles

    def data(self, item, role = ...):
        match role:
            case DB.BaseRole:
                ret = super().data(item)
            case DB.BaseLogoRole:
                ret = super().data(item.siblingAtColumn(1))
            case DB.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(2))
            case DB.FavoriteRole:
                ret = super().data(item.siblingAtColumn(3))
            case _:
                ret = super().data(item)
        return ret

    def setData(self, index, value, role = ...):
        match role:
            case DB.BaseRole:
                ret = super().data(item)
            case DB.BaseLogoRole:
                ret = super().data(item.siblingAtColumn(1))
            case DB.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(2))
            case DB.FavoriteRole:
                ret = super().data(item.siblingAtColumn(3))
            case _:
                ret = super().data(item)

    def _set_data(self, field, value):
        state = (f'UPDATE {CryptoDatabase.CryptoPairsTB} SET {field} = {value} '
                 f'WHERE ')
        query = QSqlQuery()
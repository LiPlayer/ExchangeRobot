from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtSql import QSqlQueryModel, QSqlQuery

from Python.Constants import  CryptoPairsTable
from Python.Database import Database
from Python.Constants import CryptoPairsField as const

QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class DatabaseModel(QSqlQueryModel):
    canUpdate = Signal()
    def __init__(self):
        super().__init__()
        self._db = Database.database()
        self._db.data_updated.connect(self.canUpdate)
        self.setHeaderData(0, Qt.Orientation.Horizontal, 'id')
        self.setHeaderData(1, Qt.Orientation.Horizontal, 'exchange')
        self.setHeaderData(2, Qt.Orientation.Horizontal, 'base')
        self.setHeaderData(3, Qt.Orientation.Horizontal, 'quote')
        self.setHeaderData(4, Qt.Orientation.Horizontal, 'exchange_logo')
        self.setHeaderData(5, Qt.Orientation.Horizontal, 'base_logo')
        self.setHeaderData(6, Qt.Orientation.Horizontal, 'buy_timestamp')
        self.setHeaderData(7, Qt.Orientation.Horizontal, 'sell_timestamp')
        self.setHeaderData(8, Qt.Orientation.Horizontal, 'favorite')

        self._where = ''
        self._group_by = None
        self._order_by = ''

    def database(self):
        return self._db

    @Slot()
    def select(self):
        state = f'SELECT id, exchange, base, quote, exchange_logo, base_logo, buy_timestamp, sell_timestamp, favorite '
        state += f'FROM {CryptoPairsTable} '
        if self._where:
            state += f'WHERE {self._where} '
        if self._group_by:
            group = self._group_by[0]   # base
            aggregate_func = self._group_by[1]  # MAX
            aggregate_field = self._group_by[2] # buy_time
            state = state.replace(aggregate_field, aggregate_func + f'({aggregate_field}) as {aggregate_field}', 1)
            state += f'GROUP BY {group} '
        if self._order_by:
            state += f'ORDER BY {self._order_by} '
        state += ';'
        self.setQuery(state)

    @Slot(str)
    def where(self, condition):
        self._where = condition

    @Slot(str, str, str)
    def group_by(self, group, aggregate_func, aggregate_field):
        # EX: [base, MAX, buy_timestamp]
        self._group_by = [group, aggregate_func, aggregate_field]

    @Slot(str)
    def order_by(self, condition):
        self._order_by = condition

    @Slot()
    def roleNames(self):
        roles = {
            const.IDRole: b'id',
            const.ExchangeRole : b'exchange',
            const.BaseRole : b'base',
            const.QuoteRole : b'quote',
            const.ExchangeLogoRole : b'exchange_logo',
            const.BaseLogoRole : b'base_logo',
            const.BuyTimeRole : b'buy_timestamp',
            const.SellTimeRole: b'sell_timestamp',
            const.FavoriteRole: b'favorite'
        }
        return roles

    def data(self, item, role = ...):
        match role:
            case const.IDRole:
                ret = super().data(item.siblingAtColumn(0))
            case const.ExchangeRole:
                ret = super().data(item.siblingAtColumn(1))
            case const.BaseRole:
                ret = super().data(item.siblingAtColumn(2))
            case const.QuoteRole:
                ret = super().data(item.siblingAtColumn(3))
            case const.ExchangeLogoRole:
                ret = super().data(item.siblingAtColumn(4))
            case const.BaseLogoRole:
                ret = super().data(item.siblingAtColumn(5))
            case const.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(6))
            case const.SellTimeRole:
                ret = super().data(item.siblingAtColumn(7))
            case const.FavoriteRole:
                ret = super().data(item.siblingAtColumn(8))
            case _:
                ret = super().data(item)
        return ret

    def setData(self, index, value, role = ...):
        match role:
            case const.ExchangeRole:
                field = 'exchange'
            case const.BaseRole:
                field = 'base'
            case const.QuoteRole:
                field = 'quote'
            case const.ExchangeLogoRole:
                field = 'exchange_logo'
            case const.BaseLogoRole:
                field = 'base_logo'
            case const.BuyTimeRole:
                field = 'buy_timestamp'
            case const.SellTimeRole:
                field = 'sell_timestamp'
            case const.FavoriteRole:
                field = 'favorite'
            case _:
                field = 'favorite'
        _id = self.data(index.siblingAtColumn(0))
        state = f'UPDATE {CryptoPairsTable} SET {field} = {value} WHERE id = {_id};'
        query = QSqlQuery(state)
        ok =  query.exec()
        self.select()
        self.dataChanged.emit(index, index)
        return ok
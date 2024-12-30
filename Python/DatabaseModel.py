from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlQueryModel, QSqlQuery

from Python.Database import Database
from Python.Database import Database as DB


class DatabaseModel(QSqlQueryModel):
    def __init__(self, db: Database):
        super().__init__(db)
        _db = db
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

    def select(self):
        state = f'SELECT id, exchange, base, quote, exchange_logo, base_logo, buy_timestamp, sell_timestamp, favorite '
        state += f'FROM {Database.CryptoPairsTB} '
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

    def where(self, condition):
        self._where = condition

    def group_by(self, group, aggregate_func, aggregate_field):
        # EX: [base, MAX, buy_timestamp]
        self._group_by = [group, aggregate_func, aggregate_field]

    def order_by(self, condition):
        self._order_by = condition

    def roleNames(self):
        roles = {
            DB.IDRole: b'id',
            DB.ExchangeRole : b'exchange',
            DB.BaseRole : b'base',
            DB.QuoteRole : b'quote',
            DB.ExchangeLogoRole : b'exchange_logo',
            DB.BaseLogoRole : b'base_logo',
            DB.BuyTimeRole : b'buy_timestamp',
            DB.SellTimeRole: b'sell_timestamp',
            DB.FavoriteRole: b'favorite'
        }
        return roles

    def data(self, item, role = ...):
        match role:
            case DB.IDRole:
                ret = super().data(item.siblingAtColumn(0))
            case DB.ExchangeRole:
                ret = super().data(item.siblingAtColumn(1))
            case DB.BaseRole:
                ret = super().data(item.siblingAtColumn(2))
            case DB.QuoteRole:
                ret = super().data(item.siblingAtColumn(3))
            case DB.ExchangeLogoRole:
                ret = super().data(item.siblingAtColumn(4))
            case DB.BaseLogoRole:
                ret = super().data(item.siblingAtColumn(5))
            case DB.BuyTimeRole:
                ret = super().data(item.siblingAtColumn(6))
            case DB.SellTimeRole:
                ret = super().data(item.siblingAtColumn(7))
            case DB.FavoriteRole:
                ret = super().data(item.siblingAtColumn(8))
            case _:
                ret = super().data(item)
        return ret

    def setData(self, index, value, role = ...):
        match role:
            case DB.ExchangeRole:
                field = 'exchange'
            case DB.BaseRole:
                field = 'base'
            case DB.QuoteRole:
                field = 'quote'
            case DB.ExchangeLogoRole:
                field = 'exchange_logo'
            case DB.BaseLogoRole:
                field = 'base_logo'
            case DB.BuyTimeRole:
                field = 'buy_timestamp'
            case DB.SellTimeRole:
                field = 'sell_timestamp'
            case DB.FavoriteRole:
                field = 'favorite'
            case _:
                field = 'favorite'
        _id = self.data(index.siblingAtColumn(0))
        state = f'UPDATE {Database.CryptoPairsTB} SET {field} = {value} WHERE id = {_id};'
        query = QSqlQuery(state)
        ok =  query.exec()
        self.select()
        self.dataChanged.emit(index, index)
        return ok
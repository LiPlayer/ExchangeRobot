from dataclasses import fields

from PySide6.QtCore import Qt, Signal, Slot, Property, QByteArray
from PySide6.QtQml import QmlElement
from PySide6.QtSql import QSqlQueryModel, QSqlQuery

from Python.Constants import CurrencyTable, CurrencyFields
from Python.Database import Database
from Python.Constants import CurrencyRole as const

QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class DatabaseModel(QSqlQueryModel):
    canUpdate = Signal()
    def __init__(self):
        super().__init__()
        self._db = None
        for i, field in enumerate(CurrencyFields):
            self.setHeaderData(i, Qt.Orientation.Horizontal, field[0])

        self._where = ''
        self._group_by = None
        self._order_by = ''

    @Property(Database)
    def database(self):
        return self._db

    @database.setter
    def database(self, db):
        if self._db is db:
            return
        if self._db:
            self._db.currencies_updated.disconnect(self.canUpdate)
        self._db = db
        self._db.currencies_updated.connect(self.canUpdate)

    @Slot()
    def select(self):
        state = 'SELECT ' + ', '.join([f'{field[0]}' for field in CurrencyFields]) + ' '
        state += f'FROM {CurrencyTable} '
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
        role = Qt.ItemDataRole.UserRole + 1
        roles = {}
        for i, field in enumerate(CurrencyFields):
            roles[role + i] = QByteArray(field[0])
        return roles

    def data(self, item, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        ret = super().data(item.siblingAtColumn(offset))
        return ret

    def setData(self, index, value, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        field = CurrencyFields[offset][0]
        _id = self.data(index.siblingAtColumn(0))
        state = f'UPDATE {CurrencyTable} SET {field} = {value} WHERE id = {_id};'
        query = QSqlQuery(state)
        ok =  query.exec()
        self.select()
        self.dataChanged.emit(index, index)
        return ok
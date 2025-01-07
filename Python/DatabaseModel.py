from PySide6.QtCore import Qt, Signal, Slot, Property, QByteArray
from PySide6.QtQml import QmlElement
from PySide6.QtSql import QSqlQueryModel, QSqlQuery, QSqlTableModel

from Python.Constants import CurrencyTable, CurrencyFields, OrderTaskFields, OrderTaskTable, OrderTable, OrderFields
from Python.Database import  Database

QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class CurrenciesModel(QSqlTableModel):

    def __init__(self):
        super().__init__()
        self._db = None
        for i, field in enumerate(CurrencyFields):
            self.setHeaderData(i, Qt.Orientation.Horizontal, field[0])

        self._where = ''
        self._group_by = None
        self._order_by = ''

    @Property(Database)
    def db(self):
        return self._db

    @db.setter
    def db(self, db):
        self._db = db
        self.select()
        self._db.currencies_updated.connect(self.select)

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
        return super().setData(index.siblingAtColumn(offset), value)

    def selectStatement(self):
        state = 'SELECT ' + ', '.join([f'{field[0]}' for field in CurrencyFields]) + ' '
        state += f'FROM {CurrencyTable} '
        if self._where:
            state += f'WHERE {self._where} '
        if self._group_by:
            group = self._group_by[0]  # base
            aggregate_func = self._group_by[1]  # MAX
            aggregate_field = self._group_by[2]  # buy_time
            state = state.replace(aggregate_field, aggregate_func + f'({aggregate_field}) as {aggregate_field}', 1)
            state += f'GROUP BY {group} '
        if self._order_by:
            state += f'ORDER BY {self._order_by} '
        state += ';'
        return state


@QmlElement
class OrderModel(QSqlTableModel):

    def __init__(self):
        super().__init__()
        self._db = None
        for i, field in enumerate(OrderTable):
            self.setHeaderData(i, Qt.Orientation.Horizontal, field[0])

    @Property(Database)
    def db(self):
        return self._db

    @db.setter
    def db(self, db:Database):
        self._db = db
        self._db.order_added.connect(self.select)
        self._db.order_updated.connect(self.select)
        self._db.order_removed.connect(self.select)
        self.setTable(OrderTable)
        self.select()

    @Slot()
    def roleNames(self):
        role = Qt.ItemDataRole.UserRole + 1
        roles = {}
        for i, field in enumerate(OrderFields):
            roles[role + i] = QByteArray(field[0])
        return roles

    def data(self, item, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        ret = super().data(item.siblingAtColumn(offset))
        return ret

    def setData(self, index, value, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        return super().setData(index.siblingAtColumn(offset), value)

@QmlElement
class OrderTaskModel(QSqlTableModel):

    def __init__(self):
        super().__init__()
        self._db = None
        for i, field in enumerate(OrderTaskTable):
            self.setHeaderData(i, Qt.Orientation.Horizontal, field[0])

    @Property(Database)
    def db(self):
        return self._db

    @db.setter
    def db(self, db:Database):
        self._db = db
        self._db.order_task_added.connect(self.select)
        self._db.order_task_updated.connect(self.select)
        self._db.order_task_removed.connect(self.select)
        self.setTable(OrderTaskTable)
        self.select()

    @Slot()
    def roleNames(self):
        role = Qt.ItemDataRole.UserRole + 1
        roles = {}
        for i, field in enumerate(OrderTaskFields):
            roles[role + i] = QByteArray(field[0])
        return roles

    def data(self, item, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        ret = super().data(item.siblingAtColumn(offset))
        return ret

    def setData(self, index, value, role = ...):
        offset = role - Qt.ItemDataRole.UserRole - 1
        return super().setData(index.siblingAtColumn(offset), value)
import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug, Qt
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtWidgets import QTableView

from Python.CryptoDatabase import CryptoDatabase
from Python.utils import get_timestamp


class NewListingsModel(QSqlTableModel):
    def __init__(self, db: CryptoDatabase):
        super().__init__(db)
        _db = db
        self.setTable(CryptoDatabase.CryptoPairsTB)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.setHeaderData(0, Qt.Orientation.Horizontal, 'base')
        self.setHeaderData(1, Qt.Orientation.Horizontal, 'base_logo')
        self.setHeaderData(2, Qt.Orientation.Horizontal, 'buy_timestamp')
        self.setHeaderData(3, Qt.Orientation.Horizontal, 'favorite')

        _db.data_updated.connect(self._on_updated)
    def _on_updated(self):
        self.select()

    def selectStatement(self):
        now = get_timestamp()
        state = (f'SELECT base, base_logo, MAX(buy_timestamp) AS timestamp, favorite '
                 f'FROM {CryptoDatabase.CryptoPairsTB} '
                 f'WHERE buy_timestamp > {now} '
                 f'GROUP BY base '
                 f'ORDER BY timestamp ASC;')
        return state

    def data(self, idx, role = ...):
        ret = super().data(idx, role)
        return ret
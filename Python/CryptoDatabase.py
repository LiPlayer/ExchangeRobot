import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug, Slot
from PySide6.QtSql import QSqlDatabase

from Python.GateAPI.GateRest import GateCommon
from Python.RestClient import CryptoPair


class CryptoDatabase(QObject):
    db_name = 'CryptoDB.db'
    def __init__(self):
        super().__init__()
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(self.db_name)
        if not db.open():
            qDebug(db.lastError().text())
            sys.exit(-1)

        self._gate = GateCommon()
        self._gate.all_crypto_pairs_updated.connect(self._on_all_crypto_pairs_updated)
        self._update_database()

    def _update_database(self):
        self._gate.request_all_crypto_pairs()

    @Slot(list)
    def _on_all_crypto_pairs_updated(self, pairs: list[CryptoPair]):
        pass
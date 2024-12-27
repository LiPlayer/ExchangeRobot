import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug
from PySide6.QtSql import QSqlDatabase

from Python.CryptoDatabase import CryptoDatabase


class ListingExchangeModel(QObject):
    def __init__(self, db: CryptoDatabase):
        super().__init__(db)
        _db = db
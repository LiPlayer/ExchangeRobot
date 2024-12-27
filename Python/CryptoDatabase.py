import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug, Slot, Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from Python.GateAPI.GateRest import GateCommon
from Python.RestClient import CryptoPair

class CryptoDatabase(QObject):
    ExchangeRole = Qt.ItemDataRole.UserRole + 1
    BaseRole = Qt.ItemDataRole.UserRole + 2
    QuoteRole = Qt.ItemDataRole.UserRole + 3
    ExchangeLogoRole = Qt.ItemDataRole.UserRole + 4
    BaseLogoRole = Qt.ItemDataRole.UserRole + 5
    BuyTimeRole = Qt.ItemDataRole.UserRole + 6
    SellTimeRole = Qt.ItemDataRole.UserRole + 7
    FavoriteRole = Qt.ItemDataRole.UserRole + 8

    # db_name = 'CryptoDB.db'
    db_name = ':memory:'
    CryptoPairsTB = 'CryptoPairs'
    data_updated = Signal()
    def __init__(self):
        super().__init__()
        self._db = QSqlDatabase.addDatabase('QSQLITE')
        self._db.setDatabaseName(self.db_name)
        if not self._db.open():
            qDebug(self._db.lastError().text())
            sys.exit(-1)

        # Create the CryptoPair table if not exist
        create_table_query = """
           CREATE TABLE IF NOT EXISTS CryptoPairs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               exchange TEXT NOT NULL,
               base TEXT NOT NULL,
               quote TEXT NOT NULL,
               exchange_logo TEXT,
               base_logo TEXT,
               buy_timestamp INTEGER,
               sell_timestamp INTEGER,
               favorite BOOLEAN,
               UNIQUE(exchange, base, quote)
           );
           """
        query = QSqlQuery(self._db)
        query.exec(create_table_query)
           
        self._gate = GateCommon()
        self._gate.all_crypto_pairs_updated.connect(self._on_all_crypto_pairs_updated)
        self._update_database()

    def _update_database(self):
        self._gate.request_all_crypto_pairs()

    @Slot(list)
    def _on_all_crypto_pairs_updated(self, pairs: list[CryptoPair]):
        query = QSqlQuery(self._db)
        query_str = """
          INSERT INTO CryptoPairs (
                            exchange, base, quote, exchange_logo, base_logo, buy_timestamp, sell_timestamp, favorite
                        ) VALUES (
                            :exchange, :base, :quote, :exchange_logo, :base_logo, :buy_timestamp, :sell_timestamp, 0
                        )
                        ON CONFLICT(exchange, base, quote) DO UPDATE SET
                        buy_timestamp = :buy_timestamp,
                        sell_timestamp = :sell_timestamp;
                        """
        query.prepare(query_str)
        for pair in pairs:
            query.bindValue(":exchange", pair.exchange)
            query.bindValue(":base", pair.base)
            query.bindValue(":quote", pair.quote)
            query.bindValue(":exchange_logo", pair.exchange_logo)
            query.bindValue(":base_logo", pair.base_logo)
            query.bindValue(":buy_timestamp", pair.buy_timestamp)
            query.bindValue(":sell_timestamp", pair.sell_timestamp)
            query.exec()
        if len(pairs):
            self.data_updated.emit()

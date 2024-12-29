import os
import sys

from PySide6.QtCore import QObject, Signal, QDateTime, qDebug, Slot, Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlDriver

from Python.BinanceAPI.BinanceRest import BinanceCommon
from Python.BitgetAPI.BitgetRest import BitgetCommon
from Python.BybitAPI.BybitRest import BybitCommon
from Python.EXMOAPI.EXMORest import EXMOCommon
from Python.GateAPI.GateRest import GateCommon
from Python.MEXCAPI.MexcRest import MexcCommon
from Python.RestClient import CryptoPair
from Python.XTAPI.XTRest import XTCommon


def backup_memory_to_disk(memory_db, disk_path):
    if not memory_db.isOpen():
        print("In-memory database is not open")
        return False

    # Attach the disk-based database
    query = QSqlQuery(memory_db)
    query.exec(f"ATTACH DATABASE '{disk_path}' AS disk_db")

    # Query the schema of each table from memory
    query.exec("SELECT name, sql FROM sqlite_master WHERE type='table';")
    while query.next():
        table_name = query.value(0)
        create_statement = query.value(1)

        # Recreate the table on disk_db
        create_statement = create_statement.replace(table_name, f"disk_db.{table_name}", 1)
        query.exec(create_statement)

        # Copy data from memory to disk
        if not query.exec(f"DELETE FROM disk_db.{table_name}"):
            print(f"Failed to clear table {table_name} on disk: {query.lastError().text()}")
            continue

        if not query.exec(f"INSERT INTO disk_db.{table_name} SELECT * FROM {table_name}"):
            print(f"Failed to copy data for table {table_name}: {query.lastError().text()}")
        else:
            print(f"Copied table {table_name} to {disk_path}")

    # Detach the disk-based database
    query.exec("DETACH DATABASE disk_db")
    print(f"Backup sqlite from memory to {disk_path} completed")

    return True

def load_disk_to_memory(disk_path):
    # Create in-memory database
    memory_db = QSqlDatabase.addDatabase("QSQLITE")
    memory_db.setDatabaseName(":memory:")
    if not memory_db.open():
        print("Failed to open in-memory database")
        return None

    # Attach the disk-based database
    query = QSqlQuery(memory_db)
    if not query.exec(f"ATTACH DATABASE '{disk_path}' AS disk_db;"):
        print(f"Failed to attach database: {query.lastError().text()}")
        return None

    # Query the schema of each table in the disk-based database
    if not query.exec("SELECT name, sql FROM disk_db.sqlite_master WHERE type='table';"):
        print(f"Failed to query schema: {query.lastError().text()}")
        return None

    while query.next():
        table_name = query.value(0)
        create_statement = query.value(1)

        # Recreate the table on the in-memory database
        if not query.exec(create_statement):
            print(f"Failed to create table {table_name}: {query.lastError().text()}")
            continue

        # Copy the data
        if not query.exec(f"INSERT INTO {table_name} SELECT * FROM disk_db.{table_name};"):
            print(f"Failed to copy data for table {table_name}: {query.lastError().text()}")
            continue

        print(f"Copied table {table_name} with constraints to memory database")

    # Detach the disk-based database
    query.exec("DETACH DATABASE disk_db")
    print(f"Load sqlite from {disk_path} to memory completed")

    return memory_db

class Database(QObject):
    IDRole = Qt.ItemDataRole.UserRole + 1
    ExchangeRole = Qt.ItemDataRole.UserRole + 2
    BaseRole = Qt.ItemDataRole.UserRole + 3
    QuoteRole = Qt.ItemDataRole.UserRole + 4
    ExchangeLogoRole = Qt.ItemDataRole.UserRole + 5
    BaseLogoRole = Qt.ItemDataRole.UserRole + 6
    BuyTimeRole = Qt.ItemDataRole.UserRole + 7
    SellTimeRole = Qt.ItemDataRole.UserRole + 8
    FavoriteRole = Qt.ItemDataRole.UserRole + 9

    db_name = 'CryptoDB.db'
    CryptoPairsTB = 'CryptoPairs'
    data_updated = Signal()
    def __init__(self):
        super().__init__()
        if os.path.exists(self.db_name):
            self._db = load_disk_to_memory(self.db_name)
        else:   # create database for first time
            self._db = QSqlDatabase.addDatabase('QSQLITE')
            self._db.setDatabaseName(":memory:")
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

        self._exchanges = [BinanceCommon(), BitgetCommon(), BybitCommon(), EXMOCommon(), GateCommon(), MexcCommon(),
                           XTCommon()]
        for exchange in self._exchanges:
            exchange.all_crypto_pairs_updated.connect(self._on_all_crypto_pairs_updated)

    def __del__(self):
        backup_memory_to_disk(self._db, self.db_name)

    @Slot()
    def refresh(self):
        for exchange in self._exchanges:
            exchange.request_all_crypto_pairs()

    @Slot(list)
    def _on_all_crypto_pairs_updated(self, pairs: list[CryptoPair]):
        query = QSqlQuery(self._db)
        query_str = """
          INSERT INTO CryptoPairs (
                            exchange, base, quote, exchange_logo, base_logo, buy_timestamp, sell_timestamp, favorite
                        ) VALUES (
                            :exchange, :base, :quote, :exchange_logo, :base_logo, :buy_timestamp, :sell_timestamp, :favorite
                        )
                        ON CONFLICT(exchange, base, quote) DO UPDATE SET
                        exchange_logo = excluded.exchange_logo,
                        base_logo = excluded.base_logo,
                        buy_timestamp = excluded.buy_timestamp,
                        sell_timestamp = excluded.sell_timestamp;
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
            query.bindValue(":favorite", 0)
            if not query.exec():
                print(query.lastError())
        if len(pairs):
            self.data_updated.emit()

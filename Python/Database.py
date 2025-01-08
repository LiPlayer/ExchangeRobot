import os
import sys

from PySide6.QtCore import QObject, Signal, qDebug, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QmlElement, QmlSingleton
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from Python.Constants import DatabaseName, CurrencyTable, SqlCurrency, CurrencyFields, OrderTaskFields, SqlOrderTask, \
    OrderTaskTable, SqlOrder, OrderFields, OrderTable


def backup_memory_to_disk(memory_db, disk_path):
    if not memory_db.isOpen():
        print("In-memory database is not open")
        return False

    # Attach the disk-based database
    query0 = QSqlQuery(memory_db)
    query0.exec(f"ATTACH DATABASE '{disk_path}' AS disk_db")

    # Query the schema of each table from memory
    query0.exec("SELECT name, sql FROM sqlite_master WHERE type='table';")
    while query0.next():
        table_name = query0.value(0)
        if table_name == 'sqlite_sequence' or table_name == OrderTable:
            continue
        create_statement = query0.value(1)

        query_disk = QSqlQuery(memory_db)
        # Recreate the table on disk_db
        create_statement = create_statement.replace(table_name, f"disk_db.{table_name}", 1)
        query_disk.exec(create_statement)

        # Copy data from memory to disk
        if not query_disk.exec(f"DELETE FROM disk_db.{table_name}"):
            print(f"Failed to clear table {table_name} on disk: {query_disk.lastError().text()}")
            continue

        if not query_disk.exec(f"INSERT INTO disk_db.{table_name} SELECT * FROM {table_name}"):
            print(f"Failed to copy data for table {table_name}: {query_disk.lastError().text()}")
        else:
            print(f"Copied table {table_name} to {disk_path}")

    # Detach the disk-based database
    query0.exec("DETACH DATABASE disk_db")
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
        if table_name == 'sqlite_sequence':
            continue
        create_statement = query.value(1)

        query_mem = QSqlQuery(memory_db)
        # Recreate the table on the in-memory database
        if not query_mem.exec(create_statement):
            print(f"Failed to create table {table_name}: {query_mem.lastError().text()}")
            continue

        # Copy the data
        if not query_mem.exec(f"INSERT INTO {table_name} SELECT * FROM disk_db.{table_name};"):
            print(f"Failed to copy data for table {table_name}: {query_mem.lastError().text()}")
            continue

        print(f"Copied table {table_name} with constraints to memory database")

    # Detach the disk-based database
    query.exec("DETACH DATABASE disk_db")
    print(f"Load sqlite from {disk_path} to memory completed")

    return memory_db

QML_IMPORT_NAME = "ExchangeRobot.Python"
QML_IMPORT_MAJOR_VERSION = 1

# Notice: Database won't save Orders to disk, it will always fetch the online data from API
@QmlElement
@QmlSingleton
class Database(QObject):
    currencies_updated = Signal()
    order_added = Signal()
    order_updated = Signal()
    order_removed = Signal()
    order_task_added = Signal()
    order_task_updated = Signal()
    order_task_removed = Signal()

    _db = None
    @classmethod
    def warm_up(cls):
        if os.path.exists(DatabaseName):
            cls._db = load_disk_to_memory(DatabaseName)
        else:   # create database for first time
            cls._db = QSqlDatabase.addDatabase('QSQLITE')
            cls._db.setDatabaseName(":memory:")
            if not cls._db.open():
                qDebug(cls._db.lastError().text())
                sys.exit(-1)
            cls._create_tables()

    @classmethod
    def _create_tables(cls):
        # Currency Table
        field_definitions = ', '.join([f'{field[0]} {field[1]}' for field in CurrencyFields])
        create_table_query = f"""
                             CREATE TABLE IF NOT EXISTS {CurrencyTable} (
                                 {field_definitions},
                                 UNIQUE(exchange, base, quote)
                             );
                             """
        query = QSqlQuery(cls._db)
        query.exec(create_table_query)

        # Order Task Table
        field_definitions = ', '.join([f'{field[0]} {field[1]}' for field in OrderTaskFields])
        create_table_query = f"""
                             CREATE TABLE IF NOT EXISTS {OrderTaskTable} (
                                 {field_definitions},
                                 UNIQUE(task_id, exchange)
                             );
                             """
        query = QSqlQuery(cls._db)
        query.exec(create_table_query)

        # Order Table
        field_definitions = ', '.join([f'{field[0]} {field[1]}' for field in OrderFields])
        create_table_query = f"""
                               CREATE TABLE IF NOT EXISTS {OrderTable} (
                                   {field_definitions},
                                   UNIQUE(order_id, exchange)
                               );
                               """
        query = QSqlQuery(cls._db)
        query.exec(create_table_query)

    def __init__(self):
        super().__init__()
        self._exchanges = []
        QGuiApplication.instance().aboutToQuit.connect(self.backup)


    def __del__(self):
        self.backup()


    @Slot()
    def backup(self):
        backup_memory_to_disk(self._db, DatabaseName)

    def update_balances(self):
        pass

    @Slot(list)
    def update_currencies(self, pairs: list[SqlCurrency]):
        query = QSqlQuery(self._db)
        fields = ', '.join([f'{field[0]}' for field in CurrencyFields[1:]])
        placeholders = ', '.join([f':{field[0]}' for field in CurrencyFields[1:]])

        query_str = f"""
              INSERT INTO {CurrencyTable} (
                                {fields}
                            ) VALUES (
                                {placeholders}
                            )
                            ON CONFLICT(exchange, base, quote) DO UPDATE SET
                                exchange_logo = excluded.exchange_logo,
                                base_logo = excluded.base_logo,
                                buy_timestamp = excluded.buy_timestamp,
                                sell_timestamp = excluded.sell_timestamp
                            """
        query.prepare(query_str)
        self._db.transaction()

        for pair in pairs:
            for field in CurrencyFields[1:]:
                query.bindValue(f":{field[0]}", getattr(pair, field[0], None))
            if not query.exec():
                print(query.lastError())

        self._db.commit()
        if pairs:
            self.currencies_updated.emit()

    @Slot(SqlOrderTask)
    def add_order_task(self, task:SqlOrderTask):
        query = QSqlQuery(self._db)
        fields = ', '.join([f'{field[0]}' for field in OrderTaskFields])
        placeholders = ', '.join([f':{field[0]}' for field in OrderTaskFields])

        query_str = f"""
                    INSERT INTO {OrderTaskTable} (
                        {fields}
                    ) VALUES (
                        {placeholders}
                    )
                    """
        query.prepare(query_str)

        for field in OrderTaskFields:
            query.bindValue(f":{field[0]}", getattr(task, field[0], None))

        if not query.exec():
            print(query.lastError())

        self.order_task_added.emit()

    @Slot(SqlOrderTask)
    def update_order_task(self, task):
        query = QSqlQuery(self._db)

        fields = ', '.join([f'{field[0]}=:{field[0]}' for field in OrderTaskFields])
        query_str = f"""
                    UPDATE {OrderTaskTable}
                    SET {fields}
                    WHERE task_id={task.task_id} and exchange=\'{task.exchange}\';
                    """
        query.prepare(query_str)

        # Binding values dynamically
        for field in OrderTaskFields:
            query.bindValue(f":{field[0]}", getattr(task, field[0]))

        if not query.exec():
            print(query.lastError())

        self.order_task_updated.emit()

    @Slot(SqlOrderTask)
    def remove_order_task(self, task):
        query = QSqlQuery(self._db)
        query_str = f"""
                    DELETE from {OrderTaskTable}
                    WHERE task_id={task.task_id} AND exchange=\'{task.exchange}\';
                    """
        if not query.exec(query_str):
            print(query.lastError())
        self.order_task_removed.emit()


    def get_order_task(self, exchange):
        query = QSqlQuery(self._db)
        fields = ', '.join([f'{field[0]}=:{field[0]}' for field in OrderTaskFields])
        query_str = f"""
                    SELECT {fields}
                    FROM {OrderTaskTable}
                    WHERE exchange={exchange};
                    """
        if not query.exec(query_str):
            print(query.lastError())

        tasks = []
        while query.next():
            values = [query.value(i) for i in range(len(OrderTaskFields))]
            task = SqlOrderTask(*values)
            tasks.append(task)
        return tasks

    @Slot(SqlOrder)
    def add_order(self, order: SqlOrder):
        query = QSqlQuery(self._db)

        fields = ', '.join([field[0] for field in OrderFields])
        placeholders = ', '.join([f":{field[0]}" for field in OrderFields])

        query_str = f"""
                    INSERT INTO {OrderTable} ({fields})
                    VALUES ({placeholders})
                    """
        query.prepare(query_str)

        # Bind values dynamically
        for field in OrderFields:
            query.bindValue(f":{field[0]}", getattr(order, field[0]))

        if not query.exec():
            print(query.lastError())

        self.order_added.emit()

    @Slot(SqlOrder)
    def update_order(self, order: SqlOrder):
        query = QSqlQuery(self._db)

        fields = ', '.join([f'{field[0]}=:{field[0]}' for field in OrderFields])
        query_str = f"""
                    UPDATE {OrderTable}
                    SET {fields}
                    WHERE order_id={order.order_id} AND exchange=\'{order.exchange}\';
                    """
        query.prepare(query_str)

        # Bind values dynamically
        for field in OrderFields:
            query.bindValue(f":{field[0]}", getattr(order, field[0]))

        if not query.exec():
            print(query.lastError())

        self.order_updated.emit()

    @Slot(SqlOrder)
    def remove_order(self, order: SqlOrder):
        query = QSqlQuery(self._db)
        query_str = f"""
                    DELETE from {OrderTable}
                    WHERE task_id={order.order_id} AND exchange=\'{order.exchange}\';
                    """
        if not query.exec(query_str):
            print(query.lastError())
        self.order_removed.emit()

    def get_order(self, exchange, order_id):
        query = QSqlQuery(self._db)
        fields = ', '.join([f'{field[0]}=:{field[0]}' for field in OrderFields])
        query_str = f"""
                    SELECT {fields}
                    FROM {OrderTaskTable}
                    WHERE order_id={order_id} AND exchange=\'{exchange}\';
                    """
        if not query.exec(query_str):
            print(query.lastError())

        task = None
        if query.next():
            values = [query.value(i) for i in range(len(OrderFields))]
            task = SqlOrder(*values)
        return task
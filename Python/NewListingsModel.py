from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlQuery

from Python.Database import Database
from Python.Database import Database as DB
from Python.DatabaseModel import DatabaseModel
from Python.utils import get_timestamp


class NewListingsModel(DatabaseModel):
    def __init__(self, db: Database):
        super().__init__(db)

        db.data_updated.connect(self._on_updated)
        self._on_updated()

    def _on_updated(self):
        now = get_timestamp()
        self.where(f'buy_timestamp > {now}')
        self.group_by('base', 'MAX', 'buy_timestamp')
        self.order_by('buy_timestamp ASC')
        self.select()
from PySide6.QtCore import Slot
from PySide6.QtSql import QSqlQuery

from Python.Database import Database
from Python.Database import Database as DB
from Python.DatabaseModel import DatabaseModel
from Python.utils import get_timestamp


class ListingExchangeModel(DatabaseModel):
    def __init__(self, db: Database):
        super().__init__(db)
        self._crypto = ''

        db.data_updated.connect(self._on_updated)
        self._on_updated()

    def _on_updated(self):
        if not self._crypto:
            return
        self.where(f'base = \'{self._crypto}\'')
        self.order_by('buy_timestamp ASC')
        self.select()

    @Slot(str)
    def setCrypto(self, crypto):
        self._crypto = crypto
        self._on_updated()

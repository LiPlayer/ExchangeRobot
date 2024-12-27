
import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QTableView

from Python.CryptoDatabase import CryptoDatabase
from Python.ListingExchangesModel import ListingExchangeModel
from Python.NewListingsModel import NewListingsModel
from autogen.settings import url, import_paths

if __name__ == '__main__':
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    db = CryptoDatabase()
    engine.setInitialProperties({
        'newListingsModel': NewListingsModel(db),
        'listingExchangesModel': ListingExchangeModel(db)
    })
    engine.load(os.fspath(app_dir/url))
    # view = QTableView()
    # view.setModel(NewListingsModel(db))
    # view.show()
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

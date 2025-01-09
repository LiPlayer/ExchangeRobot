
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide6.QtQuickControls2 import QQuickStyle

from Python.Database import Database
from Python.autogen.settings import url, import_paths
import os
import sys
from pathlib import Path
# import resources_rc

if __name__ == '__main__':
    QQmlDebuggingEnabler.enableDebugging(True)

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("LiPlayer")
    app.setOrganizationDomain("li.player")
    app.setApplicationName("ExchangeRobot")
    app.setWindowIcon(QIcon('://ExchangeRobotContent/images/logo.ico'))

    engine = QQmlApplicationEngine()
    Database.warm_up()

    app_dir = Path(__file__).parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

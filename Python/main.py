
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide6.QtQuickControls2 import QQuickStyle
from autogen.settings import url, import_paths
import os
import sys
from pathlib import Path
# PYTHON PATH
script_path = os.path.abspath(__file__)
root_directory = os.path.dirname(os.path.dirname(script_path))
sys.path.append(root_directory)

if __name__ == '__main__':
    QQmlDebuggingEnabler.enableDebugging(True)

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("LiPlayer")
    app.setOrganizationDomain("li.player")
    app.setApplicationName("ExchangeRobot")
    app.setWindowIcon(QIcon('://ExchangeRobotContent/images/logo.ico'))

    # Don't remove this line
    # Don't remove this line
    # Don't remove this line
    import QMLModule

    engine = QQmlApplicationEngine()

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

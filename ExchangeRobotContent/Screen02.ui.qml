

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import ExchangeRobot
import QtQuick.Controls 6.8
import QtQuick.Layouts

Rectangle {
    width: 400
    height: 80

    color: Constants.backgroundColor

    RowLayout {
        id: rowLayout
        anchors.fill: parent

        Image {
            id: _image
            horizontalAlignment: Image.AlignHCenter
            source: "qrc:/qtquickplugin/images/template_image.png"
            Layout.preferredHeight: 64
            Layout.preferredWidth: 64
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            sourceSize.height: 64
            sourceSize.width: 64
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: _text
            text: qsTr("DOGE/USDT")
            font.pixelSize: 48
            horizontalAlignment: Text.AlignHCenter
            font.styleName: "Regular"
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
        }
    }
}

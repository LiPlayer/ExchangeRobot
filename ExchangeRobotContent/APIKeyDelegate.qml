import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 360
    height: 200

    property string exchange: ""
    property string apiKey: _api_key.text
    property string apiSecret: _secret_key.text
    property string passphrase: _passphrase.text

    Settings {
        category: root.exchange
        property alias api_key: root.apiKey
        property alias secret_key: root.apiSecret
        property alias passphrase: root.passphrase
    }


    GridLayout {
        id: gridLayout
        anchors.fill: parent
        rows: 4
        columns: 2



        Text {
            id: _text
            text: root.exchange
            font.pixelSize: 20
            Layout.columnSpan: 2
        }



        Text {
            id: _text1
            text: qsTr("api key")
            font.pixelSize: 12
        }

        TextField {
            id: _api_key
            placeholderText: qsTr("API Key")
            text: root.apiKey
        }

        Text {
            id: _text2
            text: qsTr("secret key")
            font.pixelSize: 12
        }

        TextField {
            id: _secret_key
            placeholderText: qsTr("Secret Key")
            text: root.apiSecret
        }



        Text {
            id: _text3
            text: qsTr("passphrase")
            font.pixelSize: 12
        }

        TextField {
            id: _passphrase
            placeholderText: qsTr("Passphrase")
            text: root.passphrase
        }

    }

}

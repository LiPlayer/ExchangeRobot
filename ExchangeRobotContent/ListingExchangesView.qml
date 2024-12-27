import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ExchangeRobot

Pane {
    id: root
    width: Constants.width
    height: Constants.height
    property alias crypto: _crypto.text
    property alias model: listView.model

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        spacing: 20

        Text {
            id: _crypto
            width: 147
            height: 34
            text: qsTr("BTC")
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: true
            font.bold: true
        }

        ListView {
            id: listView
            width: 160
            height: 80
            spacing: 5
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: listingExchangeDummyModel
            delegate: ListingExchangeDelegate {
                width: parent.width
                exchange: model.exchange
                logo: model.logo
                timestamp: model.timestamp
            }
        }
    }

    onCryptoChanged: if (crypto.length()) model.setCrypto(crypto)
}

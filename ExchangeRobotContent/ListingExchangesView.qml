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
            clip: true
            spacing: 5
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: listingExchangeDummyModel
            delegate: ListingExchangeDelegate {
                width: listView.width
                exchange: model.exchange
                exchange_logo: model.exchange_logo
                coin_logo: model.base_logo
                timestamp: model.buy_timestamp
                star.checked: model.favorite
                star.onClicked: model.favorite = (model.favorite ? 0 : 1)
            }
        }
    }

    onCryptoChanged: if (crypto !== "") model.setCrypto(crypto)
}

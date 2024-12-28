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
                required property string exchange
                required property string exchange_logo
                required property double buy_timestamp
                width: parent.width
                name: exchange
                logo: exchange_logo
                timestamp: buy_timestamp
                onLogoChanged: {
                    console.log(logo)
                }
            }
        }
    }

    onCryptoChanged: if (crypto !== "") model.setCrypto(crypto)
}

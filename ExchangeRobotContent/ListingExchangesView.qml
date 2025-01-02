import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ExchangeRobot

Pane {
    id: root
    width: metrics.width
    height: metrics.height
    property alias crypto: _title.text
    property alias model: listView.model

    SizeMetrics {
        id: metrics
        width: 360
        height: 640
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        spacing: 20

        Text {
            id: _title
            width: 147
            height: 34
            text: qsTr("BTC")
            font.pixelSize: 30 * metrics.realScale
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
            spacing: 10
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: listingExchangeDummyModel
            delegate: ListingExchangeDelegate {
                width: listView.width
                exchange: model.exchange
                exchange_logo: model.exchange_logo
                quote: model.quote
                base_logo: model.base_logo
                timestamp: model.buy_timestamp
                star.checked: model.favorite
                star.onClicked: model.favorite = (model.favorite ? 0 : 1)
            }
        }
    }

    Drawer {
        id: drawer

        width: root.width
        height: edit.implicitHeight
        edge: Qt.BottomEdge

        OrderEdit {
            id: edit
            anchors.fill: parent
            anchors.leftMargin: drawer.width * 0.1
            anchors.rightMargin: drawer.width * 0.1
        }
    }
    onCryptoChanged: if (crypto !== "") model.setCrypto(crypto)
}

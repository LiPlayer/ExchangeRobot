import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import Inputs

Pane {
    id: root
    width: metrics.width
    height: metrics.height
    implicitWidth: metrics.width
    implicitHeight: metrics.height

    property string base: "DOGE"
    property string quote: "USDT"
    property double price: 0.0
    property double quantity: 0
    property int pricePrecision: 2
    property int quantityPrecision: 3
    property double balance: 100

    signal buyClicked()
    signal sellClicked()

    padding: 0

    SizeMetrics {
        id: metrics
        width: 360
        height: 300
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: layout
        anchors.fill: parent
        spacing: 2
        ToggleButton {
            id: _side
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        ComboBox {
            id: _type
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: ["Limit", "Market"]
        }

        LimitOrder {
            id: _limit_order
            Layout.fillHeight: true
            Layout.fillWidth: true
            base: root.base

            quote: root.quote
            price: root.price
            quantity: root.quantity
            pricePrecision: root.pricePrecision
            quantityPrecision: root.quantityPrecision
            balance: root.balance
        }


        RowLayout {
            id: rowLayout
            width: 100
            height: 100
            Layout.fillHeight: true
            Layout.fillWidth: true

            Text {
                id: _avail
                text: qsTr("Avail.")
                font.pixelSize: 14 * metrics.realScale
                color: "grey"
            }


            Text {
                id: _text1
                text: root.balance
                font.pixelSize: 14 * metrics.realScale
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                Layout.fillWidth: true
            }
        }

        Button {
            id: _place
            text: qsTr("Buy")
            Layout.fillHeight: true
            Layout.fillWidth: true
            onClicked: {
                if (_side.current === "Buy") {
                    root.buyClicked()
                } else {
                    root.buyClicked()
                }
            }
        }
    }


}

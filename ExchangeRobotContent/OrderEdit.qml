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

    readonly property alias side: _side.current
    readonly property double timestamp: new Date(_datetime.text).getTime()
    property string base: "DOGE"
    property string quote: "USDT"
    property double price: 0.0
    property double quantity: 0
    property int pricePrecision: 2
    property int quantityPrecision: 3
    property double baseBalance: 100
    property double quoteBalance: 200
    signal buyClicked()
    signal sellClicked()

    padding: 0

    SizeMetrics {
        id: metrics
        width: 360
        height: 330
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: layout
        anchors.fill: parent
        spacing: 2
        ToggleButton {
            id: _side
            Layout.rightMargin: 30
            Layout.leftMargin: 30
            Layout.fillHeight: true
            Layout.fillWidth: true
            onCurrentChanged: root
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
            side: _side.current
            onSideChanged: console.log(side)
            base: root.base
            quote: root.quote
            price: root.price
            quantity: root.quantity
            pricePrecision: root.pricePrecision
            quantityPrecision: root.quantityPrecision
            baseBalance: root.baseBalance
            quoteBalance: root.quoteBalance
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
                text: {
                    if (root.side === "Buy") {
                        let asset = root.quote
                        let bal = root.quoteBalance
                        return qsTr("%1(%2)").arg(bal).arg(asset)
                    } else {
                        let asset = root.base
                        let bal = root.baseBalance
                        return qsTr("%1(%2)").arg(bal).arg(asset)
                    }

                }
                font.pixelSize: 14 * metrics.realScale
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                Layout.fillWidth: true
            }
        }


        RowLayout {
            Layout.preferredWidth: root.width
            Layout.fillWidth: true
            Text {
                id: _text
                text: qsTr("Timer:")
                font.pixelSize: 12 * metrics.realScale
            }

            Switch {
                id: _timer
            }
            TextField {
                id: _datetime
                enabled: _timer.checked ? 1: 0
                opacity: _timer.checked ? 1: 0
                placeholderText: "2025-01-10 13:30:00"
                text: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
                font.pixelSize: 12 * metrics.realScale
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredHeight: 23
            }

            RoundButton {
                id: _place
                text: _side.current
                Layout.rightMargin: 10 * metrics.realScale
                Layout.preferredHeight: 30 * metrics.realScale
                Layout.preferredWidth: 60 * metrics.realScale
                radius: 10 * metrics.realScale
                leftPadding: 20 * metrics.realScale
                rightPadding: 20 * metrics.realScale
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
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


}

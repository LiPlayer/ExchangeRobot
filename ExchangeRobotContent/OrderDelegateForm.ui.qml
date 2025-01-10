import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import Buttons

Rectangle {
    id: root
    width: metrics.width
    height: metrics.height
    property alias _cancel: _cancel
    implicitWidth: metrics.width
    implicitHeight: metrics.height

    property int order_id: 0
    property string exchange: "Gate.io"
    property string base: "DOGE"
    property string quote: "USDT"
    property string side: "Buy"
    property string type: "Limit"
    property double timestamp: 1735640513000
    property double price: 0.7
    property double fill_price: 0.32
    property double filled: 390
    property double quantity: 390
    property string status: "open"

    SizeMetrics {
        id: metrics
        width: 360
        height: 80
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 5
        anchors.bottomMargin: 5
        spacing: 2

        RowLayout {
            id: rowLayout1
            Layout.preferredHeight: 17
            Layout.fillHeight: true
            spacing: 30 * metrics.realScale
            Layout.fillWidth: true

            Text {
                id: _exchange
                text: root.exchange
                font.pixelSize: 12 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _symbol
                text: root.base + "/" + root.quote
                font.pixelSize: _exchange.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Item {
                implicitWidth: _status.width
                Layout.fillWidth: true
                Layout.fillHeight: true
                BorderButton {
                    id: _cancel
                    visible: root.status == "open"
                    anchors.right: parent.right
                    width: 45 * metrics.realScale
                    height: parent.height
                    text: "Cancel"
                    font.pixelSize: _exchange.font.pixelSize * 0.8
                }
                Text {
                    id: _status
                    visible: root.status != "open"
                    anchors.right: parent.right
                    height: parent.height
                    text: root.status
                    font.pixelSize: _symbol.font.pixelSize
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                }
            }
        }

        RowLayout {
            id: rowLayout
            Layout.preferredHeight: 17
            spacing: 20 * metrics.realScale
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                id: _side
                color: "#c75a71"
                text: root.side === 0 ? qsTr("Sell") : "Buy"
                font.pixelSize: 12 * metrics.realScale
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: (implicitWidth + 20) * metrics.realScale
                background: Rectangle {
                    anchors.fill: parent
                    color: "#fbf4f0"
                    border.color: "#b4f6da"
                }
            }

            Label {
                id: _type
                text: root.type
                color: "#353746"
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: (implicitWidth + 20) * metrics.realScale
                background: Rectangle {
                    anchors.fill: parent
                    color: "#efeef3"
                    border.color: "#efeef3"
                }
            }

            Label {
                id: _timestamp
                text: Qt.formatDateTime(new Date(root.timestamp),
                                        "yyyy-MM-dd hh:mm:ss:zzz")
                color: "#929292"
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                font.bold: false
                Layout.fillHeight: true
                Layout.fillWidth: true
            }
        }

        GridLayout {
            id: gridLayout
            Layout.preferredHeight: 34
            rowSpacing: 0
            Layout.fillHeight: true
            Layout.fillWidth: true
            rows: 2
            columns: 3

            Text {
                id: _price_title
                color: "#979b9e"
                text: qsTr("Price")
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price_title
                color: "#979b9e"
                text: qsTr("Fill Price")
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount_title
                color: "#979b9e"
                text: qsTr("Filled/Amount")
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.preferredWidth: 100
            }

            Text {
                id: _price
                text: root.price !== "" ? root.price : root.type
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price
                text: root.fill_price
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount
                text: root.filled + "/" + root.quantity
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillHeight: true
                Layout.fillWidth: true
            }
        }
    }

    Rectangle {
        id: rectangle
        width: gridLayout.width
        height: 1
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        color: "lightgray"
    }
}

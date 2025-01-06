import QtQuick
import QtQuick.Controls
import ExchangeRobot
import QtQuick.Layouts

Rectangle {
    id: root
    width: metrics.width
    height: metrics.height
    implicitWidth: metrics.width
    implicitHeight: metrics.height

    property alias exchange_logo: _exchange_logo.source
    property string base: "DOGE"
    property string quote: "USDT"
    property string result: "All Filled"
    property string side: "Buy"
    property string type: "Limit"
    property double timestamp: 1735640513000
    property string order_price: ""
    property string fill_price: "0.417"
    property string filled: "390"
    property string total: "390"

    SizeMetrics {
        id: metrics
        width: 360
        height: 120
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        spacing: 0

        RowLayout {
            id: rowLayout1
            spacing: 30 * metrics.realScale
            Layout.preferredHeight: 70
            Layout.fillHeight: true
            Layout.fillWidth: true

            Image {
                id: _exchange_logo
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.preferredHeight: 32 * metrics.realScale
                Layout.preferredWidth: 32 * metrics.realScale
                fillMode: Image.PreserveAspectFit
            }

            Text {
                id: _symbol
                text: root.base + "/" + root.quote
                font.pixelSize: 20 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _result
                text: "Secceed"
                font.pixelSize: _symbol.font.pixelSize
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        RowLayout {
            id: rowLayout
            spacing: 20 * metrics.realScale
            Layout.preferredHeight: 70
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                id: _side
                color: "#c75a71"
                text: root.side === 0 ? qsTr("Sell") : "Buy"
                font.pixelSize: 16 * metrics.realScale
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                Layout.preferredHeight: implicitHeight * metrics.realScale
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
                Layout.preferredHeight: implicitHeight * metrics.realScale
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
                                        "yyyy-MM-dd hh:mm:ss")
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
            width: 100
            height: 100
            rowSpacing: 0
            Layout.preferredHeight: 100
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
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price_title
                color: "#979b9e"
                text: qsTr("Quantity")
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount_title
                color: "#979b9e"
                text: qsTr("Amount")
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredWidth: 100
            }

            Text {
                id: _price
                text: "0.59"
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price
                text: "500"
                font.pixelSize: _side.font.pixelSize
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount
                text: "390"
                font.pixelSize: _side.font.pixelSize
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }
        }
    }
}

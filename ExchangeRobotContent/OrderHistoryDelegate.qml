import QtQuick
import QtQuick.Controls
import ExchangeRobot
import QtQuick.Layouts

Rectangle {
    id: root
    width: metrics.width
    height: metrics.height

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
        width: Constants.width
        height: 250
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
                width: 100
                height: 100
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.preferredHeight: 48 * metrics.realScale
                Layout.preferredWidth: 48 * metrics.realScale
                fillMode: Image.PreserveAspectFit
            }

            Text {
                id: _symbol
                text: root.base + "/" + root.quote
                font.pixelSize: 38 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                font.bold: true
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _result
                text: root.result
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
                text: root.side == 0 ? qsTr("Sell") : "Buy"
                font.pixelSize: 30 * metrics.realScale
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
                font.pixelSize: 30 * metrics.realScale
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
                text: Qt.formatDateTime(new Date(root.timestamp), "yyyy-MM-dd hh:mm:ss")
                color: "#929292"
                font.pixelSize: 30 * metrics.realScale
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
            Layout.preferredHeight: 140
            Layout.fillHeight: true
            Layout.fillWidth: true
            rows: 2
            columns: 3

            Text {
                id: _price_title
                color: "#979b9e"
                text: qsTr("Price")
                font.pixelSize: 38 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price_title
                color: "#979b9e"
                text: qsTr("Fill Price")
                font.pixelSize: 38 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 100
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount_title
                color: "#979b9e"
                text: qsTr("Filled/Amount")
                font.pixelSize: 38 * metrics.realScale
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
                Layout.preferredWidth: 100
            }

            Text {
                id: _price
                text: root.order_price != "" ? root.order_price : root.type
                font.pixelSize: 38 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }

            Text {
                id: _fill_price
                text: root.fill_price
                font.pixelSize: 38 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }

            Text {
                id: _filled_amount
                text: root.filled + "/" + root.total
                font.pixelSize: 38 * metrics.realScale
                horizontalAlignment: Text.AlignRight
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
            }
        }

    }
}

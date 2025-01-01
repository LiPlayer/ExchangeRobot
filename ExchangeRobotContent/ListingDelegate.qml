import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import "Utils.js" as Utils

AbstractButton {
    id: root
    width: metrics.width
    height: metrics.height
    property alias exchange_logo: _exchange_logo.source
    property alias base: _base.text
    property alias quote: _quote.text
    property alias base_logo: _base_logo.source
    property alias star: _star
    property double timestamp: 0

    focusPolicy: Qt.ClickFocus
    display: AbstractButton.TextOnly

    SizeMetrics {
        id: metrics
        width: 360
        height: 60
        realWidth: root.width
        realHeight: root.height
    }


    background: Rectangle {
        id: bg
        color: "#f9f3e1"
        radius: 10
        states: [
            State {
                name: "pressed"
                when: root.pressed
                PropertyChanges {
                    target: bg
                    color: Qt.lighter(Qt.color("#f9f3e1"), 1.1)
                }
            },
            State {
                name: "hovered"
                when: root.hovered
                PropertyChanges {
                    target: bg
                    color: Qt.lighter(Qt.color("#f9f3e1"), 1.05)
                }
            }
        ]
    }

    GridLayout {
        id: gridLayout
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 5
        anchors.bottomMargin: 5
        columnSpacing: 5
        rows: 2
        columns: 4
        flow: GridLayout.TopToBottom

        Image {
            id: _base_logo
            source: "qrc:/qtquickplugin/images/template_image.png"
            sourceSize.height: Layout.preferredHeight
            sourceSize.width: Layout.preferredWidth
            Layout.rowSpan: 2
            Layout.preferredHeight: 48 * metrics.realScale
            Layout.preferredWidth: 48 * metrics.realScale
            fillMode: Image.PreserveAspectFit
        }

        RowLayout {
            id: rowLayout
            spacing: 5
            Layout.preferredWidth: 150
            Layout.fillHeight: true
            Layout.fillWidth: true

            Text {
                id: _quote
                text: qsTr("USDT")
                font.pixelSize: 12 * metrics.realScale
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 50
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            Image {
                id: _exchange_logo
                horizontalAlignment: Image.AlignLeft
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.preferredWidth: 50
                sourceSize.height: 16 * metrics.realScale
                sourceSize.width: 16 * metrics.realScale
                Layout.fillHeight: false
                Layout.fillWidth: true
                Layout.preferredHeight: 16 * metrics.realScale
                fillMode: Image.PreserveAspectFit
            }
        }

        Text {
            id: _base
            text: qsTr("BTC...............")
            font.pixelSize: 20 * metrics.realScale
            verticalAlignment: Text.AlignVCenter
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: 150
        }

        Text {
            id: _start_time
            color: "#f79824"
            font.pixelSize: 16 * metrics.realScale
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: _countdown
            color: "#f79824"
            font.pixelSize: 20 * metrics.realScale
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("1D 01:22:30")
        }

        RoundButton {
            id: _star
            visible: true
            Layout.fillHeight: false
            Layout.preferredHeight: 32 * metrics.realScale
            Layout.preferredWidth: 32 * metrics.realScale
            flat: true
            display: AbstractButton.IconOnly
            padding: 0
            icon {
                source: "images/star-o.svg"
                color: "black"
            }

            Layout.rowSpan: 2
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            states: [
                State {
                    name: "isStar"
                    when: _star.checked
                    PropertyChanges {
                        _star.icon.source: "images/star.svg"
                        _star.icon.color: "#f4ea2a"
                    }
                }
            ]
        }
    }
    onTimestampChanged: {
        _start_time.text = Qt.formatDateTime(new Date(root.timestamp), "yyyy-MM-dd hh:mm:ss")
        updateCountdown()
    }

    Component.onCompleted: {
        Constants.timer.triggered.connect(updateCountdown)
    }

    Component.onDestruction: {
        Constants.timer.triggered.disconnect(updateCountdown)
    }

    function updateCountdown() {
        let countdown = Utils.getCountdown(root.timestamp);
        _countdown.text = countdown;
    }
}



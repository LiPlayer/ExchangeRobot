import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import "Utils.js" as Utils

AbstractButton {
    id: root
    width: Constants.width * Constants.realScale
    height: 160 * Constants.realScale
    property alias exchange_logo: _exchange_logo.source
    property alias base: _base.text
    property alias quote: _quote.text
    property alias base_logo: _base_logo.source
    property alias star: _star
    property double timestamp: 0

    focusPolicy: Qt.ClickFocus
    display: AbstractButton.TextOnly

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
        anchors.leftMargin: root.width / 30
        anchors.rightMargin: root.width / 30
        anchors.topMargin: root.height / 20
        anchors.bottomMargin: root.height / 20
        columnSpacing: root.width / 20
        rows: 2
        columns: 4
        flow: GridLayout.TopToBottom

        Image {
            id: _base_logo
            width: 48
            height: 48
            source: "qrc:/qtquickplugin/images/template_image.png"
            sourceSize.height: 48
            sourceSize.width: 48
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.rowSpan: 2
            Layout.preferredHeight: 48
            Layout.preferredWidth: 48
            fillMode: Image.PreserveAspectFit
        }

        RowLayout {
            id: rowLayout
            Layout.preferredWidth: 150
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: 20 * Constants.realScale

            Text {
                id: _quote
                text: qsTr("USDT")
                font.pixelSize: _base_logo.height / 4
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: false
                Layout.fillHeight: true
            }

            Image {
                id: _exchange_logo
                horizontalAlignment: Image.AlignRight
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                Layout.preferredWidth: 32
                fillMode: Image.PreserveAspectFit
            }
        }

        Text {
            id: _base
            text: qsTr("BTC...............")
            font.pixelSize: _base_logo.height / 2.5
            verticalAlignment: Text.AlignVCenter
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: 150
        }

        Text {
            id: _start_time
            color: "#f79824"
            font.pixelSize: _quote.font.pixelSize
            horizontalAlignment: Text.AlignRight
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: _countdown
            color: "#f79824"
            font.pixelSize: _base.font.pixelSize
            horizontalAlignment: Text.AlignRight
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("1D 01:22:30")
        }

        RoundButton {
            id: _star
            visible: true
            Layout.fillHeight: false
            Layout.preferredHeight: 64 * Constants.realScale
            Layout.preferredWidth: 64 * Constants.realScale
            Layout.fillWidth: false
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



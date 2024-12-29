import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import "Utils.js" as Utils

AbstractButton {
    id: root
    width: 600
    height: 100
    property alias exchange: _exchange.text
    property alias exchange_logo: _exchange_logo.source
    property alias coin_logo: _coin_logo.source
    property alias star: _star
    property double timestamp: 0

    focusPolicy: Qt.ClickFocus
    display: AbstractButton.TextOnly


    background: Rectangle {
        id: bg
        color: "#f9f3e1"
        radius: 10
        property double _currentTime: 0
        states: [
            State {
                name: "outdated"
                when: root.timestamp < bg._currentTime
                PropertyChanges {
                    target: bg
                    opacity: 0.6
                }
            },
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
        columnSpacing: 10
        rows: 2
        columns: 3
        flow: GridLayout.LeftToRight

        Image {
            id: _exchange_logo
            width: 48
            height: 48
            source: "qrc:/qtquickplugin/images/template_image.png"
            Layout.rowSpan: 2
            Layout.preferredWidth: 100
            Layout.fillHeight: true
            Layout.fillWidth: true
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: _exchange
            text: qsTr("BTC......")
            font.pixelSize: _exchange_logo.height / 2
            verticalAlignment: Text.AlignVCenter
            Layout.preferredHeight: 40
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: 200
        }

        RowLayout {
            id: rowLayout1
            width: 100
            height: 100
            Layout.fillHeight: true
            Layout.preferredWidth: 100
            Layout.fillWidth: true

            Image {
                id: _coin_logo
                width: 20
                height: 20
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.preferredHeight: 32
                Layout.preferredWidth: 150
                fillMode: Image.PreserveAspectFit
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            RoundButton {
                id: _star
                width: 48
                height: 48
                visible: true
                Layout.fillWidth: false
                Layout.fillHeight: false
                icon.color: "black"
                flat: true
                display: AbstractButton.IconOnly
                icon.source: "images/star-o.svg"
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

        Text {
            id: _start_time
            color: "#f79824"
            font.pixelSize: _exchange_logo.height / 4
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            Layout.preferredHeight: 20
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: _countdown
            color: "#f79824"
            font.pixelSize: _exchange_logo.height / 3.5
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            Layout.preferredWidth: 100
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("1D 01:22:30")
        }







    }
    onTimestampChanged: {
        _start_time.text = Qt.formatDateTime(new Date(root.timestamp), "yyyy-MM-dd hh:mm:ss")
        updateCountdown()
    }

    Component.onCompleted: {
        Constants.timer.triggered.connect(updateCountdown)
        bg._currentTime = new Date().getTime();
    }

    Component.onDestruction: {
        Constants.timer.triggered.disconnect(updateCountdown)
    }

    function updateCountdown() {
        let countdown = Utils.getCountdown(root.timestamp);
        _countdown.text = countdown;
    }
}

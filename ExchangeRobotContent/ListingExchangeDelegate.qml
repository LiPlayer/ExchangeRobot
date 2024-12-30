import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot
import "Utils.js" as Utils

AbstractButton {
    id: root
    width: Constants.width * Constants.realScale
    height: 160 * Constants.realScale
    property alias exchange: _exchange.text
    property alias exchange_logo: _exchange_logo.source
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
        property double _currentTime: 0
        states: [
            State {
                name: "outdated"
                when: root.timestamp < bg._currentTime
                PropertyChanges {
                    target: root
                    opacity: 0.5
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
        anchors.leftMargin: root.width / 30
        anchors.rightMargin: root.width / 30
        anchors.topMargin: root.height / 20
        anchors.bottomMargin: root.height / 20
        columnSpacing: root.width / 10
        rows: 2
        columns: 3
        flow: GridLayout.LeftToRight

        Image {
            id: _exchange_logo
            width: 30
            height: 30
            source: "qrc:/qtquickplugin/images/template_image.png"
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            sourceSize.height: 256
            sourceSize.width: 256
            Layout.rowSpan: 2
            Layout.preferredWidth: 60
            fillMode: Image.PreserveAspectFit
        }

        RowLayout {
            id: rowLayout
            width: 100
            height: 100
            Layout.preferredHeight: 40
            Layout.fillHeight: true
            Layout.preferredWidth: 180
            Layout.fillWidth: true

            Text {
                id: _exchange
                text: qsTr("Bitget")
                font.pixelSize: _exchange_logo.height / 2
                // font.pixelSize: 10
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 120
                Layout.fillHeight: true
                Layout.fillWidth: true
            }

            Text {
                id: _quote
                text: qsTr("USDT")
                font.pixelSize: _exchange_logo.height / 4
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                Layout.preferredWidth: 60
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        RowLayout {
            id: rowLayout1
            width: 100
            height: 100
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            Layout.preferredHeight: 40
            Layout.fillHeight: true
            Layout.preferredWidth: 60
            Layout.fillWidth: true

            Image {
                id: _base_logo
                width: 20
                height: 20
                horizontalAlignment: Image.AlignRight
                source: "qrc:/qtquickplugin/images/template_image.png"
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                Layout.preferredHeight: 40
                Layout.preferredWidth: 40
                fillMode: Image.PreserveAspectFit
                Layout.fillWidth: true
                Layout.fillHeight: true
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
            font.pixelSize: _exchange_logo.height / 3
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            Layout.preferredHeight: 20
            Layout.preferredWidth: 180
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: _countdown
            color: "#f79824"
            font.pixelSize: _exchange_logo.height / 3
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            Layout.preferredHeight: 20
            Layout.preferredWidth: 120
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

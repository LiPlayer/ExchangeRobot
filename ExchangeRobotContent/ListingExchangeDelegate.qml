import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot

AbstractButton {
    id: root
    width: 600
    height: 60
    property alias name: _exchange.text
    property alias logo: _logo.source
    property double timestamp: 0

    focusPolicy: Qt.ClickFocus
    display: AbstractButton.TextOnly

    QtObject {
        id: _data
        property double now: 0
        Component.onCompleted: {
            var currentTime = new Date().getTime(); // Current time in milliseconds
            now = currentTime
        }
    }

    background: Rectangle {
        id: bg
        color: "#f9f3e1"
        radius: 10
        states: [
            State {
                name: "started"
                when: timestamp < _data.now
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
        x: 2
        y: -6
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        columnSpacing: 40
        rows: 2
        columns: 4
        flow: GridLayout.TopToBottom

        Image {
            id: _logo
            width: 100
            height: 100
            source: "images/mexc_logo.svg"
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.margins: 10
            Layout.rowSpan: 2
            Layout.preferredHeight: 64
            Layout.preferredWidth: 150
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: _exchange
            text: qsTr("Exchange")
            font.pixelSize: _logo.height / 1.5
            verticalAlignment: Text.AlignVCenter
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: 150
            Layout.rowSpan: 2
        }

        Text {
            id: _start_time
            color: "#f79824"
            font.pixelSize: _logo.height / 2
            horizontalAlignment: Text.AlignRight
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: _countdown
            color: "#f79824"
            font.pixelSize: _logo.height / 2
            horizontalAlignment: Text.AlignRight
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: qsTr("1D 01:22:30")
        }
    }

    onTimestampChanged: {
        _start_time.text = Qt.formatDateTime(new Date(timestamp), "yyyy-MM-dd hh:mm:ss")
    }

    Component.onCompleted: {
        Constants.timer.triggered.connect(updateCountdown);
    }
    Component.onDestruction: {
        Constants.timer.triggered.disconnect(updateCountdown)
    }

    // Helper function to ensure two-digit format
    function pad(value) {
        return value < 10 ? "0" + value : value;
    }

    function updateCountdown() {
        var currentTime = new Date().getTime(); // Current time in milliseconds
        var timeDiff = root.timestamp - currentTime; // Time difference in milliseconds

        if (timeDiff <= 0) {
            _countdown.text = "00:00:00"; // If time is up, return 00:00:00
            return
        }

        var days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        var hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

        // Format as 'days hh:mm:ss'
        var ret = days + "D " + pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);

        _countdown.text = ret;
    }
}

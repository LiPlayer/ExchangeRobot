import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ExchangeRobot

AbstractButton {
    id: root
    width: 600
    height: 80
    property alias coin: coin.text
    property alias logo: logo.source
    property int timestamp: 0

    focusPolicy: Qt.ClickFocus
    display: AbstractButton.TextOnly

    background: Rectangle {
        id: bg
        color: "#f9f3e1"
        radius: 5
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
            id: logo
            width: 100
            height: 100
            source: "qrc:/qtquickplugin/images/template_image.png"
            Layout.rowSpan: 2
            Layout.preferredHeight: 64
            Layout.preferredWidth: 64
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: coin
            text: qsTr("BTC")
            font.pixelSize: logo.height / 2
            Layout.fillWidth: true
            Layout.preferredWidth: 150
            Layout.rowSpan: 2
        }

        Text {
            id: start_time
            color: "#f79824"
            font.pixelSize: logo.height / 2.5
            horizontalAlignment: Text.AlignRight
            Layout.fillWidth: true
            text: qsTr("2024-12-20 15:00:00")
        }

        Text {
            id: countdown
            color: "#f79824"
            font.pixelSize: logo.height / 2.5
            horizontalAlignment: Text.AlignRight
            Layout.fillWidth: true
            text: qsTr("1D 01:22:30")
        }

        RoundButton {
            id: star
            width: 48
            height: 48
            visible: true
            text: "+"
            icon.color: "black"
            flat: true
            display: AbstractButton.IconOnly
            icon.source: "images/star-o.svg"
            checkable: true
            Layout.rowSpan: 2
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            states: [
                State {
                    name: "isStar"
                    when: star.checked
                    PropertyChanges {
                        star {
                            icon.source: "images/star.svg"
                            icon.color: "#f4ea2a"
                        }
                    }
                }
            ]
        }
    }

    onTimestampChanged: {
        start_time.text = Qt.formatDateTime(new Date(timestamp), "yyyy-MM-dd hh:mm:ss")
    }

    Component.onCompleted: {
        Constants.timer.triggered.connect(updateCountdown);
    }

    function updateCountdown() {
        var currentTime = new Date().getTime(); // Current time in milliseconds
        var timeDiff = timestamp - currentTime; // Time difference in milliseconds

        if (timeDiff <= 0) {
            return "00:00:00"; // If time is up, return 00:00:00
        }

        var days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        var hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

        // Format as 'days hh:mm:ss'
        ret = days + "D " + pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);

        countdown.text = ret;
    }

    // Helper function to ensure two-digit format
    function pad(value) {
        return value < 10 ? "0" + value : value;
    }
}

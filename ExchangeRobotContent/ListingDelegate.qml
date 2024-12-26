import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 600
    height: 80
    color: "#f9f3e1"
    radius: 5
    property alias coin: coin.text
    property alias logo: logo.source
    property date time

    GridLayout {
        id: gridLayout
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
                    PropertyChanges {
                        star {
                            icon.source: "images/star.svg"
                            icon.color: "#f4ea2a"
                        }
                    }
                }
            ]
            state: checked ? 'isStar' : ''
        }
    }


}

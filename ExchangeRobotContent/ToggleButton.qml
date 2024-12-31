import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Studio.Components
import ExchangeRobot

Item {
    id: root
    width: metrics.width
    height: metrics.height
    property string current: group.checkedButton.text

    SizeMetrics {
        id: metrics
        width: 300
        height: 40
        realWidth: root.width
        realHeight: root.height
    }

    ButtonGroup {
        id: group
        buttons: rowLayout.children
    }

    component SideButton : AbstractButton {
            id: button
            text: qsTr("Side")
            font.pixelSize: 20 * metrics.realScale
            checkable: true
            background: Rectangle {
                color: parent.checked ? "#26bb7b" : "#eeeff3"
                radius: 20 * metrics.realScale
            }
            contentItem: Text {
                text: parent.text
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                color: parent.checked ? "white" : "black"
                font.pixelSize: 20 * metrics.realScale
            }
    }

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        spacing: 10 * metrics.realScale

        SideButton {
            id: _buy_button
            checked: true
            text: "Buy"
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        SideButton {
            id: _sell_button
            checked: false
            text: "Sell"
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
    }
}

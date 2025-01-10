import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 360
    height: 40

    property int currentIndex : 0
    onCurrentIndexChanged: {
        for (let i = 0; i < group.buttons.length; i++) {
            let item = group.buttons[i];
            if (i === currentIndex && !item.checked) {
                item.checked = true
                return
            }
        }
    }


    ButtonGroup {
        id: group
        buttons: layout.children
        onCheckedButtonChanged: {
            for (let i = 0; i < buttons.length; i++) {
                let item = buttons[i];
                if (item.checked) {
                    currentIndex = i;
                    return
                }
            }
        }
    }

    RowLayout {
        id: layout
        anchors.fill: parent
        RoundButton {
            text: "Order"
            icon.source: "../images/star.svg"
            display: AbstractButton.TextUnderIcon
            flat: true
            padding: 0
            font.pixelSize: 8
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            checkable: true
            Layout.fillHeight: false
            Layout.fillWidth: false
        }
        RoundButton {
            text: "Trade"
            icon.source: "../images/star.svg"
            display: AbstractButton.TextUnderIcon
            flat: true
            padding: 0
            font.pixelSize: 8
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            checked: true
            checkable: true
            Layout.fillHeight: false
            Layout.fillWidth: false
        }
        RoundButton {
            text: "Account"
            icon.source: "../images/star.svg"
            display: AbstractButton.TextUnderIcon
            flat: true
            padding: 0
            font.pixelSize: 8
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            checkable: true
            Layout.fillHeight: false
            Layout.fillWidth: false
        }
    }
}

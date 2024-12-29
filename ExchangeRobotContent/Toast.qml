import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle {
    id: toast
    property alias text: message.text
    property int duration: 3000
    width: 200
    height: 50

    visible: false
    opacity: 0
    radius: 10
    color: "#323232"

    TextMetrics {
        id: metrics
    }

    onTextChanged: {
        metrics.text = message.text
        metrics.font = message.font
        toast.width = Math.min(metrics.width + 40, parent.width * 0.9)
        toast.height = metrics.height + 40
        showToast()
    }

    Text {
        id: message
        text: "Toast Message"
        color: "white"
        font.pixelSize: 16
        wrapMode: Text.Wrap
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        anchors.centerIn: parent
        padding: 10
    }

    function showToast() {
        toast.visible = true
        toast.opacity = 0
        fadeIn.start()
        dismiss.start()
    }

    SequentialAnimation {
        id: dismiss
        PauseAnimation { duration: toast.duration }
        ScriptAction {
            script: toast.visible = false
        }
    }

    PropertyAnimation {
        id: fadeIn
        target: toast
        property: "opacity"
        from: 0
        to: 1
        duration: 500
    }
}
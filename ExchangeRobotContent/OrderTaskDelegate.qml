import QtQuick
import ExchangeRobot
import "Utils.js" as Utils

OrderTaskDelegateForm {
    id: root
    property int taskId: 0
    width: implicitWidth
    height: implicitHeight
    signal cancelClicked(int taskId)
    _cancel.onClicked: {
        cancelClicked(taskId)
    }
    onTimestampChanged: {
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

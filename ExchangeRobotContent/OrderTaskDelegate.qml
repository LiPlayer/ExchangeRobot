import QtQuick

OrderTaskDelegateForm {
    property int taskId: 0
    width: implicitWidth
    height: implicitHeight
    signal cancelClicked(int taskId)
    _cancel.onClicked: {
        cancelClicked(taskId)
    }
}

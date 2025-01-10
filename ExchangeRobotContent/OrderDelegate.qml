import QtQuick
import QtQuick.Controls

OrderDelegateForm {
    property var orderId: 0
    width: implicitWidth
    height: implicitHeight
    signal cancelClicked(var orderId)
    _cancel.onClicked: {
        cancelClicked(orderId)
    }
}

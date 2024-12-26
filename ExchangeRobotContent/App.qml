import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: Constants.width
    height: Constants.height

    visible: true

    NewListingView {
        id: newListingView
        anchors.fill: parent
    }
}


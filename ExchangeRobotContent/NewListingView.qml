

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import ExchangeRobot

Pane {
    id: root
    width: Constants.width
    height: Constants.height

    signal listingClicked(crypto: string)

    ListView {
        id: listView
        anchors.fill: parent
        spacing: 5
        model: newListingDummyModel

        delegate: ListingDelegate {
            width: parent.width
            coin: model.base
            logo: model.logo
            timestamp: model.timestamp
            onClicked: root.listingClicked()
        }
    }
}

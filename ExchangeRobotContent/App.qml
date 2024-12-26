import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: Constants.width
    height: Constants.height

    visible: true

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: newListingView

        NewListingsView {
            id: newListingView
            anchors.fill: parent
        }

        ListingExchangesView {
            id: listingExchangesView
            anchors.fill: parent
        }
    }
}


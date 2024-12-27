import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: Constants.width
    height: Constants.height

    visible: true
    property string currentCrypto


    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: newListingView
    }

    Component {
        id: newListingView
        NewListingsView {
            anchors.fill: parent
            model: newListingsModel
            onListingClicked: (crypto) => {
                                  currentCrypto = crypto
                                  stackView.push(listingExchangesView)
                              }
        }
    }

    Component {
        id: listingExchangesView
        ListingExchangesView {
            anchors.fill: parent
            model: listingExchangesModel
            crypto: currentCrypto
            Button {
                id: _pop
                width: 48
                height: 48
                anchors.left: parent.left
                anchors.leftMargin: 0
                icon.source: "images/back.svg"
                display: AbstractButton.IconOnly
                flat: true
                onClicked: stackView.pop()
            }
        }
    }
}


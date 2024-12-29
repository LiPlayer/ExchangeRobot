import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: Constants.width
    height: Constants.height

    visible: true
    property string currentCrypto
    property var database
    property var newListingsModel: newListingsDummyModel
    property var listingExchangesModel: listingsExchangesDummyModel


    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: newListingView
    }

    Component {
        id: newListingView
        NewListingsView {
            model: root.newListingsModel
            onListingClicked: (crypto) => {
                                  currentCrypto = crypto
                                  stackView.push(listingExchangesView)
                              }
        }
    }

    Component {
        id: listingExchangesView
        ListingExchangesView {
            model: root.listingExchangesModel
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

    RoundButton {
        id: fresh
        text: "\u21bb"
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 10
        anchors.topMargin: 10
        flat: true

        Connections {
            target: fresh
            function onClicked() {
                database.refresh();
                toast.text = 'Start refreshing database from internet.';
                toast.showToast();
            }
        }
    }

    Toast {
        id: toast
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 100
        anchors.horizontalCenter: parent.horizontalCenter
    }
}


import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 360
    height: 640

    property string currentCrypto

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: newListingView
    }

    Component {
        id: newListingView
        NewListingsView {
            onListingClicked: (crypto) => {
                                  currentCrypto = crypto;
                                  stackView.push(listingExchangesView);
                              }
        }
    }

    Component {
        id: listingExchangesView
        ListingExchangesView {
            crypto: currentCrypto
            width: stackView.width
            height: stackView.height

            RoundButton {
                id: _pop
                width: icon.width
                height: icon.height
                anchors.leftMargin: 20 * metrics.realScale
                anchors.topMargin: 20 * metrics.realScale
                icon.height: 20 * metrics.realScale
                icon.width: 20 * metrics.realScale
                icon.source: "images/back.svg"
                display: AbstractButton.IconOnly
                flat: true
                onClicked: stackView.pop()
            }
        }
    }

    RoundButton {
        id: fresh
        width: font.pixelSize
        height: font.pixelSize
        text: "\u21bb"
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 20 * metrics.realScale
        anchors.topMargin: 20 * metrics.realScale
        padding: 0
        flat: true
        font.pixelSize: 20 * metrics.realScale

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
        anchors.bottomMargin: 100 * metrics.realScale
        anchors.horizontalCenter: parent.horizontalCenter
    }
}

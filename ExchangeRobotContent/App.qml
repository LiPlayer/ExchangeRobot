import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: Constants.width
    height: Constants.height
    onWidthChanged: Constants.realWidth = width
    onHeightChanged: Constants.realHeight = height

    property string currentCrypto
    property var database
    property var newListingsModel: newListingsDummyModel
    property var listingExchangesModel: listingsExchangesDummyModel

    visible: true
    Component.onCompleted: {
        if (Qt.platform.os === "windows" || Qt.platform.os === "linux") {
            width = 480;
            height = 640;
        } else if (Qt.platform.os === "android") {
            visibility = ApplicationWindow.FullScreen
        }
    }

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
                                  currentCrypto = crypto;
                                  stackView.push(listingExchangesView);
                              }
        }
    }

    Component {
        id: listingExchangesView
        ListingExchangesView {
            model: root.listingExchangesModel
            crypto: currentCrypto
            width: stackView.width
            height: stackView.height

            Button {
                id: _pop
                width: 64 * Constants.realScale
                height: 64 * Constants.realScale
                anchors.left: parent.left
                anchors.leftMargin: 0
                icon.height: 64
                icon.width: 64
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
        anchors.rightMargin: 10 * Constants.realScale
        anchors.topMargin: 10 * Constants.realScale
        flat: true
        font.pixelSize: 50 * Constants.realScale

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
        anchors.bottomMargin: 100 * Constants.realScale
        anchors.horizontalCenter: parent.horizontalCenter
    }
}


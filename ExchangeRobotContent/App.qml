import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: metrics.width
    height: metrics.height

    property string currentCrypto
    property var database
    property var newListingsModel: newListingsDummyModel
    property var listingExchangesModel: listingsExchangesDummyModel

    title: 'Exchange Robot'
    visible: true

    SizeMetrics {
        id: metrics
        width: Constants.width
        height: Constants.height
        realWidth: root.width
        realHeight: root.height
    }

    Image {
        id: star
        fillMode: Image.PreserveAspectFit
    }
    Component.onCompleted: {
        if (Qt.platform.os === "windows" || Qt.platform.os === "linux") {
            width = 360;
            height = 640;
        } else if (Qt.platform.os === "android") {
            visibility = ApplicationWindow.FullScreen;
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


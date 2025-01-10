import QtQuick
import QtQuick.Controls
import ExchangeRobot
import Buttons
import ExchangeRobot.Python

Window {
    id: root
    width: metrics.width
    height: metrics.height
    title: 'Exchange Robot'
    visible: true

    // Component.onCompleted: {
    //     if (Qt.platform.os === "windows" || Qt.platform.os === "linux") {
    //         width = 360;
    //         height = 640;
    //     } else if (Qt.platform.os === "android") {
    //         visibility = ApplicationWindow.FullScreen;
    //     }
    // }
    Component.onCompleted: {
        APILibrary.addApi("Gate.io", GateApi);

        let db = Database;
        let apis = APILibrary.apis()
        for (let api of apis) {
            api.db = db;
        }
    }

    SizeMetrics {
        id: metrics
        width: Constants.width
        height: Constants.height
        realWidth: root.width
        realHeight: root.height
    }

    SwipeView {
        id: swipeView
        currentIndex: nav.currentIndex
        onCurrentIndexChanged: nav.currentIndex = currentIndex
        anchors.fill: parent
        OrderView {
        }

        TradingView {

        }

        AccountView {

        }
    }
    NavigationButtons {
        id: nav
        currentIndex: 1
        anchors.bottom: parent.bottom
        width: parent.width
        onCurrentIndexChanged: swipeView.currentIndex = currentIndex
    }
}


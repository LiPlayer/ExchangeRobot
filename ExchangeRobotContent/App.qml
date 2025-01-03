import QtQuick
import QtQuick.Controls
import ExchangeRobot

Window {
    id: root
    width: metrics.width
    height: metrics.height

    property var database

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

    SizeMetrics {
        id: metrics
        width: Constants.width
        height: Constants.height
        realWidth: root.width
        realHeight: root.height
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        TradingView {

        }

        AccountView {

        }
    }
}


import QtQuick
import QtQuick.Controls
import ExchangeRobot
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
        let db = Database;
        let apis = [GateApi];
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
        anchors.fill: parent
        OrderView {
        }

        TradingView {

        }

        AccountView {

        }
    }

}


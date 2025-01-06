import QtQuick
import QtQuick.Controls
import ExchangeRobot
import ExchangeRobot.Python

Item {
    id: root
    width: metrics.width
    height: metrics.height

    SizeMetrics {
        id: metrics
        width: 360
        height: 640
        realWidth: root.width
        realHeight: root.height
    }

    TabBar {
        id: tabBar
        width: parent.width
        TabButton {
            text: "Order Tasks"
        }
        TabButton {
            text: 'Open Orders'
        }
        TabButton {
            text: 'Orders History'
        }
        TabButton {
            text: 'Trade History'
        }
    }

    SwipeView {
        anchors.top: tabBar.bottom
        anchors.bottom: root.bottom
        width: root.width
        ListView {
            model: TaskModel {
                id: _model
                db: Database
            }

            delegate: OrderTaskDelegate {
                base: model.base
                quote: model.quote
                price: model.price
                quantity: model.quantity
                timestamp: model.timestamp
                status: model.status
            }
        }
    }
}

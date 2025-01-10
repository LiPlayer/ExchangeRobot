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
        currentIndex: _swipe.currentIndex
        TabButton {
            text: "Order Tasks"
        }
        TabButton {
            text: 'Open Orders'
        }
        TabButton {
            text: 'Trade History'
        }
    }

    SwipeView {
        id: _swipe
        currentIndex: tabBar.currentIndex
        anchors.top: tabBar.bottom
        anchors.bottom: root.bottom
        width: root.width
        ListView {
            clip: true
            model: OrderTaskModel {
                db: Database
            }
            delegate: OrderTaskDelegate {
                width: _swipe.width
                taskId: model.task_id
                exchange: model.exchange
                base: model.base
                quote: model.quote
                price: model.price
                quantity: model.quantity
                timestamp: model.timestamp
                status: model.status
                onCancelClicked: {
                    APILibrary.api(model.exchange).cancel_order_task(model.task_id)
                }
            }
        }
        ListView {
            clip: true
            model: OrderModel {
                db: Database
                Component.onCompleted: {
                    where('status==\'open\'');
                    select();
                }
            }
            delegate: OrderDelegate {
                width: _swipe.width
                orderId: model.order_id
                exchange: model.exchange
                type: model.type
                side: model.side
                base: model.base
                quote: model.quote
                price: model.price
                quantity: model.quantity
                filled: model.filled_quantity
                timestamp: model.create_timestamp
                status: model.status
                onCancelClicked: {
                    APILibrary.api(model.exchange).cancel_order(model.order_id)
                }
            }
        }
        ListView {
            clip: true
            model: OrderModel {
                db: Database
                Component.onCompleted: {
                    where('status!=\'open\'');
                    select();
                }
            }
            delegate: OrderDelegate {
                width: _swipe.width
                orderId: model.order_id
                exchange: model.exchange
                type: model.type
                side: model.side
                base: model.base
                quote: model.quote
                price: model.price
                quantity: model.quantity
                filled: model.filled_quantity
                timestamp: model.create_timestamp
                status: model.status
            }
        }
    }
}

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
            model: OrderTaskModel {
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
        ListView {
            model: OrderModel {
                db: Database
                Component.onCompleted: {
                    where('status==\'open\'');
                    select();
                }
            }
            delegate: OrderDelegate {
            order_id: model.order_id
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
        ListView {
            model: OrderModel {
                db: Database
                Component.onCompleted: {
                    where('status!=\'open\'');
                    select();
                }
            }
            delegate: OrderDelegate {
            order_id: model.order_id
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

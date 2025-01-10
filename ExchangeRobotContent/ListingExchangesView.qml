import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ExchangeRobot
import ExchangeRobot.Python

Pane {
    id: root
    width: metrics.width
    height: metrics.height
    property alias crypto: _title.text
    property alias model: listView.model

    onCryptoChanged: _model.update()
    SizeMetrics {
        id: metrics
        width: 360
        height: 640
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        spacing: 20

        Text {
            id: _title
            width: 147
            height: 34
            text: qsTr("BTC")
            font.pixelSize: 30 * metrics.realScale
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: true
            font.bold: true
        }

        ListView {
            id: listView
            width: 160
            height: 80
            clip: true
            spacing: 10
            Layout.fillHeight: true
            Layout.fillWidth: true
            Component.onCompleted: _model.update()
            model: CurrenciesModel {
                id: _model
                db: Database
                function update() {
                    where('base=\'' + root.crypto + '\'')
                    order_by('buy_timestamp ASC')
                    select()
                }
            }

            delegate: ListingExchangeDelegate {
                width: listView.width
                exchange: model.exchange
                exchange_logo: model.exchange_logo
                quote: model.quote
                base_logo: model.base_logo
                timestamp: model.buy_timestamp
                star.checked: model.favorite
                star.onClicked: model.favorite = (model.favorite ? 0 : 1)
                onClicked: {
                    _drawer.open()
                    _edit.base = model.base
                    _edit.quote = model.quote
                    _edit.pricePrecision = model.price_precision
                    _edit.quantityPrecision = model.quantity_precision
                    _edit.setExchange(model.exchange)
                }
            }
        }
    }

    Drawer {
        id: _drawer

        width: root.width
        height: _edit.implicitHeight
        edge: Qt.BottomEdge

        OrderEdit {
            id: _edit
            anchors.fill: parent
            anchors.leftMargin: _drawer.width * 0.1
            anchors.rightMargin: _drawer.width * 0.1
            property var current_api: null
            property var apis: APILibrary.items()
            function setExchange(exchange) {
                if (current_api !== null) {
                    current_api.balances_updated.disconnect(updateBalance);
                }
                current_api = apis[exchange]
                current_api.balances_updated.connect(updateBalance);
            }
            function updateBalance() {
                _edit.baseBalance = current_api.balance(base)
                _edit.quoteBalance = current_api.balance(quote)

            }
            onBuyClicked: {
                place_order("Buy");
                _drawer.close()
            }
            onSellClicked: {
                place_order("Sell");
            }
            function place_order(side) {
                current_api.place_order_task(side, _edit.base, _edit.quote, _edit.price, _edit.quantity, _edit.timestamp)
            }
        }
    }
}

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import ExchangeRobot
import "../Utils.js" as Utils

Item {
    id: root
    property string side: "Buy"
    property string base: "DOGE"
    property string quote: "USDT"
    property double price: 0.0
    property double quantity: 0
    property int pricePrecision: 2
    property int quantityPrecision: 3
    property double baseBalance: 100
    property double quoteBalance: 200
    readonly property int amountPrecision: pricePrecision + quantityPrecision

    width: metrics.width
    height: metrics.height

    onSideChanged: {
        root.price = 0
        root.quantity = 0
        _percent.value = 0
    }

    onPriceChanged: {
        _price.value = root.price

        _updateAmount()
        _updatePercentage()
    }

    onQuantityChanged: {
        _quantity.value = root.quantity

        _updateAmount()
        _updatePercentage()
    }

    onBaseBalanceChanged: {
        _updatePercentage()
    }

    onQuoteBalanceChanged: {
        _updatePercentage()
    }

    function _updatePercentage() {
        if (_percent.pressed)
            return
        let ratio = 0;
        if (root.side == "Buy")
            ratio = Number(_amount) / quoteBalance;
        else
            ratio = Number(_amount) / baseBalance;
        ratio = Math.min(1, ratio);
        _percent.value = ratio;
    }

    function _updateAmount() {
        let amount = price * quantity;
        amount = Utils.floorByPrecision(amount, amountPrecision)
        _amount.text = amount.toString();
    }

    SizeMetrics {
        id: metrics
        width: 360
        height: 200
        realWidth: root.width
        realHeight: root.height
    }

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent

        FloatSpinBox {
            id: _price
            placeholderText: "Price" + '(' + root.quote + ")"
            Layout.fillHeight: true
            Layout.fillWidth: true
            value: root.price
            from: 0
            to: 100
            decimals: pricePrecision
            onValueChanged: {
                root.price = value
            }
        }

        FloatSpinBox {
            id: _quantity
            placeholderText: "Quantity" + '(' + root.base + ")"
            Layout.fillHeight: true
            Layout.fillWidth: true
            from: 0
            to: 1e8
            decimals: quantityPrecision
            value: root.quantity
            onValueChanged: {
                root.quantity = value
            }
        }

        Slider {
            id: _percent
            value: 0.0
            from: 0
            to: 1
            stepSize: 0.1
            padding: 0
            snapMode: Slider.SnapAlways
            Layout.fillHeight: true
            Layout.fillWidth: true
            onValueChanged: {
                if (root.price <= 0 || !_percent.pressed) {
                    return;
                }
                let ratio = value;
                let amount = 0;
                if (root.side === "Buy")
                    amount = root.quoteBalance * ratio;
                else
                    amount = root.baseBalance * ratio;
                let quan = amount / root.price
                root.quantity = Utils.floorByPrecision(quan, quantityPrecision);
            }
        }

        TextField {
            id: _amount
            horizontalAlignment: Text.AlignHCenter
            Layout.preferredHeight: 30
            Layout.fillHeight: true
            Layout.fillWidth: true
            placeholderText: "amount" + '(' + root.quote + ")"
            validator: DoubleValidator {
                bottom: 0
                top:  root.side === "Buy" ? root.quoteBalance : root.baseBalance
                decimals: root.pricePrecesion + root.quantityPrecesion
                notation: DoubleValidator.StandardNotation
            }
            onEditingFinished: {
                let num = Number(text);
                let amount = num / root.price;
                root.quantity = Utils.floorByPrecision(amount, quantityPrecision);
            }
        }

    }

}

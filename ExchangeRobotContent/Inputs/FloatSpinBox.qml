import QtQuick
import QtQuick.Controls
import ExchangeRobot

Item {
    id: root
    width: metrics.width
    height: metrics.height

    property double from: 0
    property double to: 10000
    property double value: 1.4
    property int decimals: 2
    property string placeholderText: "placeholder"
    onValueChanged: {
        spinbox.setValue(value)
    }

    SizeMetrics {
        id: metrics
        width: 200
        height: 32
        realWidth: root.width
        realHeight: root.height
    }

    SpinBox {
        id: spinbox
        anchors.fill: parent
        from: decimalToInt(root.from)
        value: decimalToInt(root.value)
        to: decimalToInt(root.to)
        stepSize: 1
        editable: true
        anchors.centerIn: parent
        onValueChanged: {
            if (root.placeholderText === displayText) {
                root.value = '0'
                return
            }
            root.value = value / decimalFactor
        }

        readonly property int decimalFactor: Math.pow(10, root.decimals)

        function setValue(val) {
            spinbox.value = decimalToInt(val)
        }

        function decimalToInt(decimal) {
            return Math.floor(decimal * decimalFactor + 0.5)
        }

        validator: DoubleValidator {
            bottom: Math.min(spinbox.from, spinbox.to)
            top:  Math.max(spinbox.from, spinbox.to)
            decimals: root.decimals
            notation: DoubleValidator.StandardNotation
        }

        textFromValue: function(value, locale) {
            if (value === 0) {
                return root.placeholderText
            }
            return Number(value / decimalFactor).toLocaleString(locale, 'f', root.decimals)
        }

        valueFromText: function(text, locale) {
            if (text === root.placeholderText) {
                return 0
            }
            return Math.round(Number.fromLocaleString(locale, text) * decimalFactor)
        }
    }
}

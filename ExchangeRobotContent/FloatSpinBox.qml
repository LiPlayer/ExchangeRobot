import QtQuick
import QtQuick.Controls
import ExchangeRobot

Item {
    id: root
    width: Constants.width
    height: 260 * metrics.realScale

    property int decimals: 2
    property string placeholderText: "placeholder"
    readonly property string value: spinbox.displayText

    SizeMetrics {
        id: metrics
        width: Constants.width
        height: Constants.height
        realWidth: root.width
        realHeight: root.height
    }

    SpinBox {
        id: spinbox
        anchors.fill: parent
        from: 0
        value: decimalToInt(1.1)
        to: decimalToInt(100)
        stepSize: 1
        editable: true
        anchors.centerIn: parent

        property real realValue: value / decimalFactor
        readonly property int decimalFactor: Math.pow(10, root.decimals)

        function decimalToInt(decimal) {
            return decimal * decimalFactor
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
                return 0.0
            }
            return Math.round(Number.fromLocaleString(locale, text) * decimalFactor)
        }

        contentItem: TextInput {
                 z: 2
                 text: control.textFromValue(control.value, control.locale)

                 font: control.font
                 color: "#21be2b"
                 selectionColor: "#21be2b"
                 selectedTextColor: "#ffffff"
                 horizontalAlignment: Qt.AlignHCenter
                 verticalAlignment: Qt.AlignVCenter

                 readOnly: !control.editable
                 validator: control.validator
                 inputMethodHints: Qt.ImhFormattedNumbersOnly
             }

             up.indicator: Rectangle {
                 x: control.mirrored ? 0 : parent.width - width
                 height: parent.height
                 implicitWidth: 40
                 implicitHeight: 40
                 color: control.up.pressed ? "#e4e4e4" : "#f6f6f6"
                 border.color: enabled ? "#21be2b" : "#bdbebf"

                 Text {
                     text: "+"
                     font.pixelSize: control.font.pixelSize * 2
                     color: "#21be2b"
                     anchors.fill: parent
                     fontSizeMode: Text.Fit
                     horizontalAlignment: Text.AlignHCenter
                     verticalAlignment: Text.AlignVCenter
                 }
             }

             down.indicator: Rectangle {
                 x: control.mirrored ? parent.width - width : 0
                 height: parent.height
                 implicitWidth: 40
                 implicitHeight: 40
                 color: control.down.pressed ? "#e4e4e4" : "#f6f6f6"
                 border.color: enabled ? "#21be2b" : "#bdbebf"

                 Text {
                     text: "-"
                     font.pixelSize: control.font.pixelSize * 2
                     color: "#21be2b"
                     anchors.fill: parent
                     fontSizeMode: Text.Fit
                     horizontalAlignment: Text.AlignHCenter
                     verticalAlignment: Text.AlignVCenter
                 }
             }
    }
}

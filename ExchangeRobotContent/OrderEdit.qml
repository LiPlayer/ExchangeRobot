import QtQuick
import QtQuick.Controls
import ExchangeRobot
import QtQuick.Layouts

Item {
    id: root
    width: Constants.width
    height: 1600 * metrics.realScale

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent

        ToggleButton {
            id: toggleButton
        }

        ComboBox {
            id: comboBox
            model: ["Limit", "Market"]
        }

        MySpinBox {
            id: spinBox
        }
    }
}

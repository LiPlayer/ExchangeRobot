import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 360
    height: 640

    Column {
        id: column
        anchors.fill: parent

        Repeater {
            model: ["Bitget", "Gate.io", "MEXC", "XT", "Binance"]
            delegate: APIKeyDelegate {
                exchange: modelData
            }
        }

    }

}

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
            id: _repeater
            model: ["Gate.io"]
            property var apis: [GateApi]
            delegate: APIKeyDelegate {
                exchange: modelData
                onApiKeyChanged: _repeater.apis[index].api_key = apiKey
                onApiSecretChanged: _repeater.apis[index].api_secret = apiSecret
                onPassphraseChanged: _repeater.apis[index].passphrase = passphrase
            }
        }
    }

}

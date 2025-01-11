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
            property var apis: []
            Component.onCompleted: {
                apis = APILibrary.apis();
                model = APILibrary.exchanges();
            }

            delegate: APIKeyDelegate {
                exchange: modelData
                onApiKeyChanged: {
                    _repeater.apis[index].api_key = apiKey;
                    connectServer();
                }
                onApiSecretChanged: {
                    _repeater.apis[index].api_secret = apiSecret;
                    connectServer();
                }
                onPassphraseChanged:{
                    _repeater.apis[index].passphrase = passphrase;
                    connectServer()
                }
                function connectServer() {
                    if (apiKey !== "" && apiSecret !== "") {
                        _repeater.apis[index].open()
                    }
                }
            }
        }
    }

}

pragma Singleton
import QtQuick
import QtQuick.Controls

QtObject {
    id: root
    property var apiMap: ({})
    function addApi(exchange, api) {
        apiMap[exchange] = api
    }
    function items() {
        return apiMap;
    }

    function exchanges() {
        return Object.keys(apiMap)
    }
    function api(exchange) {
        return apiMap[exchange]
    }
    function apis() {
        return Object.values(apiMap)
    }
}

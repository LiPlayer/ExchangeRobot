import QtQuick
import QtQuick.Controls
import ExchangeRobot
import QtQuick.Layouts

Pane {
    id: root
    width: Constants.width
    height: Constants.height

    property alias model: listView.model
    signal listingClicked(crypto: string)

    ColumnLayout {
        id: columnLayout
        anchors.fill: parent
        spacing: 20

        Text {
            id: _text
            width: 147
            height: 34
            text: qsTr("New Listings")
            font.pixelSize: 30
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.bold: true
            Layout.fillHeight: false
            Layout.fillWidth: true
        }

        ListView {
            id: listView
            width: 160
            height: 80
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            spacing: 5
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: newListingsDummyModel

            delegate: ListingDelegate {
                required property string base
                required property string base_logo
                required property double buy_timestamp
                required property int favorite
                width: listView.width
                name: base
                logo: base_logo
                timestamp: buy_timestamp
                star: favorite ? true : false
                onClicked: root.listingClicked(base)
                onStarChanged: favorite = (star ? 1 : 0)
            }
        }
    }
}

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
            font.pixelSize: 60 * Constants.realScale
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
            clip: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            spacing: 10
            Layout.fillHeight: true
            Layout.fillWidth: true
            model: newListingsDummyModel

            delegate: ListingDelegate {
                width: listView.width
                base: model.base
                quote: model.quote
                base_logo: model.base_logo
                exchange_logo: model.exchange_logo
                timestamp: model.buy_timestamp
                star.checked: model.favorite
                star.onClicked: model.favorite = (model.favorite ? 0 : 1)
                onClicked: root.listingClicked(base)
            }
        }
    }
}

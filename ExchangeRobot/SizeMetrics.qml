import QtQuick
import QtQuick.Controls

QtObject {
    id: root
    property int width: 1080
    property int height: 1920
    property int realWidth: width
    property int realHeight: height
    property double realScale: Math.min(realWidth / width, realHeight / height)
}

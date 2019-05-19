import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0

Item {
    id: item1
    property alias rectangle1: rectangle1
    property alias mouse1: mouse

    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
        anchors.top: parent.top

        Rectangle {
            id: rectangle1
            width: 40
            height: 40
            property color btnColor: "#c87272"
            color: btnColor
            radius: 0
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            Layout.preferredHeight: -1
            Layout.preferredWidth: -1
            Layout.fillHeight: false
            Layout.fillWidth: false

            MouseArea {
                id: mouse
                hoverEnabled: true
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
            }

            Image {
                id: image1
                width: 40
                height: 30
                fillMode: Image.PreserveAspectFit
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                source: "1479858088_add.png"
            }
        }
    }
}

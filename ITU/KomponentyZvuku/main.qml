import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0

ApplicationWindow {
    id: applicationWindow1
    visible: true
    width: 1920
    height: 1080
    title: qsTr("Ivan is awesome!")

    Rectangle {
        id: rectangle1
        color: "#c3bcbc"
        anchors.fill: parent
    }

    ColumnLayout {
        id: columnLayout1
        anchors.fill: parent
        antialiasing: false
        spacing: 5

        Item {
            id: item1
            width: 200
            height: 150
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.fillHeight: false
            Layout.fillWidth: true

            MyHeader{
                anchors.fill: parent
                Layout.fillWidth: false
            }
        }

        Item {
            id: item3
            width: 200
            height: 400
            Layout.fillWidth: true

            MyAudioView {
                id: myAudioView1
            }
        }

        Item {
            id: item2
            width: 200
            height: 200
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.fillWidth: true

            Page1{
                anchors.fill: parent
                Layout.fillWidth: false
            }
        }

    }


}

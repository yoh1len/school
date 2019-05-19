import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0

Item {
    id: item1
    width: 1920
    height: 400
    property alias playS: playS
    property alias recS: recS
    property alias stopS: stopS

    property alias rectangle6: rectangle6
    property alias mouseArea3: mouseArea3

    property alias rectangle2: rectangle2
    property alias mouseArea1: mouseArea1

    property alias mouseAreaStopS: mouseAreaStopS
    property alias mouseAreaPlayS: mouseAreaPlayS
    property alias mouseAreaRecS: mouseAreaRecS

    RowLayout {
        id: rowLayout1
        width: 100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.top: parent.top
        spacing: 0

        ColumnLayout {
            id: columnLayout1
            x: 0
            y: 0
            Layout.fillWidth: false

            RowLayout {
                id: rowLayout2
                width: 100
                height: 100
                Layout.fillHeight: false
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                Row {
                    id: row2
                    width: 300
                    height: 60
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                    Image {
                        id: image1
                        width: 60
                        height: 60
                        source: "1479773331_microphone.png"
                    }

                    Slider {
                        id: slider1
                        width: 260
                        height: 60
                        value: 0.5
                    }
                }
            }

            RowLayout {
                id: rowLayout3
                width: 100
                height: 100
                Layout.fillHeight: false

                Row {
                    id: row3
                    width: 200
                    height: 40
                    layoutDirection: Qt.LeftToRight

                    Image {
                        id: image2
                        width: 60
                        height: 60
                        source: "1479773690_seo-social-web-network-internet_150.png"
                    }

                    Slider {
                        id: slider2
                        width: 260
                        height: 60
                        value: 0.5
                    }
                }
            }

            RowLayout {
                id: rowLayout4
                Layout.fillHeight: false
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom

                Row {
                    id: row4
                    width: 300

                    Rectangle {
                        id: stopS
                        width: 60
                        height: 60
                        color: btnColor
                        property color btnColor: "#c87272"

                        Image {
                            id: image3
                            anchors.fill: parent
                            source: "ic_stop_48px-128.png"
                        }

                        MouseArea {
                            id: mouseAreaStopS
                            hoverEnabled: true
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    Rectangle {
                        id: playS
                        width: 60
                        height: 60
                        color: btnColor
                        property color btnColor: "#c87272"
                        property int sourceState: 1


                        Image {
                            id: image4
                            anchors.fill: parent
                            source: playS.sourceState ? "ic_play_arrow_48px-128.png" : "Pause_Icon-128.png"
                        }

                        MouseArea {
                            id: mouseAreaPlayS
                            hoverEnabled: true
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    Rectangle {
                        id: recS
                        width: 60
                        height: 60
                        color: btnColor
                        property color btnColor: "#c87272"

                        Image {
                            id: image5
                            anchors.fill: parent
                            source: "media-record-128.png"
                        }

                        MouseArea {
                            id: mouseAreaRecS
                            hoverEnabled: true
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }
            }
        }

        Row {
            id: row1
            width: 200
            height: 400
            Layout.fillHeight: true
            Layout.fillWidth: true

            Rectangle {
                id: rectangle1
                color: "#ffffff"
                anchors.fill: parent

                Text {
                    id: text1
                    text: qsTr("Frekvencia")
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 200

                    Rectangle {
                        id: rectangle2
                        height: 2
                        color: "#000000"
                        anchors.right: parent.right
                        anchors.rightMargin: 0
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.verticalCenter: parent.verticalCenter

                        Rectangle {
                            id: rectangle3
                            width: 60
                            height: 10
                            property color btnColor: "#2500e4"
                            color: btnColor
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                id: mouseArea1
                                anchors.fill: parent
                                drag.target: rectangle2
                                drag.axis: Drag.YAxis
                                drag.minimumY: 0
                                drag.maximumY: text1.height

                            }
                        }
                    }


                    Rectangle {
                        id: rectangle4
                        width: 2
                        color: "#000000"
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 0
                        anchors.top: parent.top
                        anchors.topMargin: 0

                        Rectangle {
                            id: rectangle5
                            width: 10
                            height: 60
                            color: "#40b21f"
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                id: mouseArea2
                                anchors.fill: parent
                                drag.target: rectangle4
                                drag.axis: Drag.XAxis
                                drag.minimumX: 0
                                drag.maximumX: text1.width
                            }
                        }
                    }

                    Rectangle {
                        id: rectangle6
                        width: 2
                        color: "#000000"
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 0
                        anchors.top: parent.top
                        anchors.topMargin: 0
                        anchors.right: parent.right
                        anchors.rightMargin: 0

                        Rectangle {
                            id: rectangle7
                            width: 10
                            height: 60
                            color: "#40b21f"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                id: mouseArea3
                                anchors.fill: parent
                                drag.target: rectangle6
                                drag.axis: Drag.XAxis
                                drag.minimumX: 0
                                drag.maximumX: text1.width
                            }
                        }
                    }
                }
            }
        }



    }
}

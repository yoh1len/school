import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0

Item {
    id: item1
    width: 1920
    height: 150
    property alias openM: openM
    property alias saveM: saveM
    property alias backM: backM
    property alias forwardM: forwardM
    property alias stopM: stopM
    property alias playM: playM
    property alias recM: recM
    property alias cutM: cutM

    property alias mouseAreaOpenM: mouseAreaOpenM
    property alias mouseAreaSaveM: mouseAreaSaveM
    property alias mouseAreaBackM: mouseAreaBackM
    property alias mouseAreaForwardM: mouseAreaForwardM
    property alias mouseAreaStopM: mouseAreaStopM
    property alias mouseAreaPlayM: mouseAreaPlayM
    property alias mouseAreaRecM: mouseAreaRecM
    property alias mouseAreaCutM: mouseAreaCutM

    property alias image6: image6


    ColumnLayout {
        id: columnLayout1
        spacing: 1
        anchors.fill: parent

        RowLayout {
            id: rowLayout1
            width: 100
            height: 50
            spacing: 5
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            Layout.fillWidth: true

            Row {
                id: row1
                width: 200
                height: 400

                Rectangle {
                    id: openM
                    width: 100
                    height: 50
                    color: btnColor
                    property color btnColor: "#c87272"
                    border.width: 1
                    Layout.fillHeight: false

                    Image {
                        id: image1
                        width: 50
                        height: 50
                        fillMode: Image.PreserveAspectFit
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        sourceSize.height: 0
                        sourceSize.width: 0
                        source: "1479753408_Open.png"
                    }

                    MouseArea {
                        id: mouseAreaOpenM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }

                Rectangle {
                    id: saveM
                    width: 100
                    height: 50
                    color: btnColor
                    property color btnColor: "#c87272"
                    border.width: 1

                    Image {
                        id: image2
                        width: 50
                        height: 50
                        fillMode: Image.PreserveAspectFit
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        source: "floppy_disk_save-128.png"
                    }

                    MouseArea {
                        id: mouseAreaSaveM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }
            }

            Row {
                id: row2
                width: 200
                height: 50

                Rectangle {
                    id: backM
                    width: 70
                    height: 50
                    color: btnColor
                    property color btnColor: "#c87272"
                    border.width: 1

                    Image {
                        id: image3
                        width: 50
                        height: 50
                        fillMode: Image.PreserveAspectFit
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        source: "1479754940_127_ArrowLeft.png"
                    }

                    MouseArea {
                        id: mouseAreaBackM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }

                Rectangle {
                    id: forwardM
                    width: 70
                    height: 50
                    color: btnColor
                    property color btnColor: "#c87272"
                    border.width: 1

                    Image {
                        id: image4
                        width: 50
                        height: 50
                        fillMode: Image.PreserveAspectFit
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        source: "1479754937_129_ArrowRight.png"
                    }

                    MouseArea {
                        id: mouseAreaForwardM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }
            }

        }

        RowLayout {
            id: rowLayout2
            width: 100
            height: 100
            Layout.rowSpan: 2

            Row {
                id: row3
                width: 200
                height: 100
                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                Layout.rowSpan: 2

                Rectangle {
                    id: stopM
                    width: 200
                    height: 100
                    color: btnColor
                    radius: 0
                    property color btnColor: "#c87272"
                    border.width: 1

                    Image {
                        id: image5
                        width: 100
                        height: 100
                        fillMode: Image.PreserveAspectFit
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        source: "ic_stop_48px-128.png"
                    }

                    MouseArea {
                        id: mouseAreaStopM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }

                Rectangle {
                    id: playM
                    width: 200
                    height: 100
                    color: btnColor
                    property color btnColor: "#c87272"
                    property int sourceState: 1

                    border.width: 1

                    Image {
                        id: image6
                        width: 100
                        height: 100
                        fillMode: Image.PreserveAspectFit
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        source: playM.sourceState ? "ic_play_arrow_48px-128.png" : "Pause_Icon-128.png"
                    }

                    MouseArea {
                        id: mouseAreaPlayM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }

                Rectangle {
                    id: recM
                    width: 200
                    height: 100
                    color: btnColor
                    property color btnColor: "#c87272"
                    border.width: 1

                    Image {
                        id: image7
                        width: 100
                        height: 100
                        fillMode: Image.PreserveAspectFit
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        source: "media-record-128.png"
                    }

                    MouseArea {
                        id: mouseAreaRecM
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        anchors.fill: parent
                    }
                }
            }

            Column {
                id: column1
                width: 300
                height: 100
                spacing: 0
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignLeft | Qt.AlignTop

                Row {
                    id: row4
                    height: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 0

                    Rectangle {
                        id: rectangle8
                        width: 50
                        height: 50
                        color: "#ffffff"
                        anchors.left: parent.left
                        anchors.leftMargin: 3

                        Image {
                            id: image8
                            width: 50
                            height: 50
                            fillMode: Image.PreserveAspectFit
                            source: "1479773331_microphone.png"
                        }
                    }

                    ComboBox {
                        id: comboBoxInM
                        width: 220
                        currentIndex: 0
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: rectangle8.right
                        anchors.leftMargin: 0
                        model: ["Default", "BlueYeti", "Realtek Media Capture"]
                    }

                    Slider {
                        id: micVolumeM
                        stepSize: 0.01
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: comboBoxInM.right
                        anchors.leftMargin: 0
                        value: 0.5
                    }

                    Rectangle {
                        id: rectangle9
                        width: 50
                        height: 50
                        color: "#ffffff"
                        anchors.left: micVolumeM.right
                        anchors.leftMargin: 0

                        Image {
                            id: image9
                            width: 50
                            height: 50
                            fillMode: Image.PreserveAspectFit
                            source: "1479773690_seo-social-web-network-internet_150.png"
                        }
                    }

                    ComboBox {
                        id: comboBoxOutM
                        width: 220
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: rectangle9.right
                        anchors.leftMargin: 0
                        model: ["Default", "Speakers", "Headphones"]
                    }

                    Slider {
                        id: outVolumeM
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: comboBoxOutM.right
                        anchors.leftMargin: 0
                        value: 0.5
                    }

                }

                Row {
                    id: row5
                    height: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 0

                    Rectangle {
                        id: cutM
                        width: 50
                        height: 50
                        color: btnColor
                        property color btnColor: "#c87272"
                        anchors.left: parent.left
                        anchors.leftMargin: 3

                        Image {
                            id: image10
                            x: 630
                            y: 0
                            width: 35
                            height: 35
                            fillMode: Image.PreserveAspectFit
                            anchors.horizontalCenter: parent.horizontalCenter
                            source: "1479774863_content-cut.png"
                        }

                        Text {
                            id: text1
                            text: qsTr("Cut")
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            font.pixelSize: 12
                        }

                        MouseArea {
                            id: mouseAreaCutM
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            anchors.fill: parent
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: mouseAreaOpenM
        onEntered: print("clicked")
    }



}

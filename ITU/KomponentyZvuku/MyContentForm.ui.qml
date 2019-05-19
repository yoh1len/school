import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
Item {
    width: 640
    height: 480
    property alias toolBar1: toolBar1

    ColumnLayout {
        id: columnLayout1
        width: 100
        height: 100
    }

    ToolBar {
        id: toolBar1
        x: 82
        y: 160
        width: 360
    }
}

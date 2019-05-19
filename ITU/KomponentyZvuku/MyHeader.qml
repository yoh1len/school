import QtQuick 2.7

MyHeaderForm {
        openM.color: mouseAreaOpenM.containsMouse ? Qt.darker(openM.btnColor) : openM.btnColor;
        saveM.color: mouseAreaSaveM.containsMouse ? Qt.darker(saveM.btnColor) : saveM.btnColor;
        backM.color: mouseAreaBackM.containsMouse ? Qt.darker(backM.btnColor) : backM.btnColor;
        forwardM.color: mouseAreaForwardM.containsMouse ? Qt.darker(forwardM.btnColor) : forwardM.btnColor;

        stopM.color: mouseAreaStopM.containsMouse ? Qt.darker(stopM.btnColor) : stopM.btnColor;
        playM.color: mouseAreaPlayM.containsMouse ? Qt.darker(playM.btnColor) : playM.btnColor;
        recM.color: mouseAreaRecM.containsMouse ? Qt.darker(recM.btnColor) : recM.btnColor;

        cutM.color: mouseAreaCutM.containsMouse ? Qt.darker(cutM.btnColor) : cutM.btnColor;

        mouseAreaPlayM.onClicked: {
            if(playM.sourceState == 1){
                playM.sourceState = 0;
            }
            else{
                playM.sourceState = 1;
            }
        }
}

import QtQuick 2.7

MyAudioViewForm {

    stopS.color: mouseAreaStopS.containsMouse ? Qt.darker(stopS.btnColor) : stopS.btnColor;
    playS.color: mouseAreaPlayS.containsMouse ? Qt.darker(playS.btnColor) : playS.btnColor;
    recS.color: mouseAreaRecS.containsMouse ? Qt.darker(recS.btnColor) : recS.btnColor;


    mouseArea3.onPressed: {
        rectangle6.anchors.right = undefined;
    }

    mouseArea1.onPressed: {
        rectangle2.anchors.verticalCenter = undefined;
    }

    mouseAreaPlayS.onClicked: {
        if(playS.sourceState == 1){
            playS.sourceState = 0;
        }
        else{
            playS.sourceState = 1;
        }
    }
}



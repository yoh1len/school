import QtQuick 2.7

Page1Form {
    button1.onClicked: {
        console.log("Button Pressed. Entered text: " + textField1.text);
    }
    rectangle1.color: mouse1.containsMouse ? Qt.darker(rectangle1.btnColor) : rectangle1.btnColor;
    mouse1.onEntered: {
        console.log("Rectangle Entered.");
    }

    mouse1.onClicked: {
        console.log("Rectangle Pressed.");
    }
}

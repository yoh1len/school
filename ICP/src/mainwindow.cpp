//! Implementation of functions for user interface logic
/*! \file mainwindow.cpp
 *  \author Jan Válka
 *  \author Ivan Eštvan
 */
#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    scene = new QGraphicsScene(this);
    ui->graphicsView->setScene(scene);
    id = 0;
    stepId = 0;
    availablePorts.append(defaultPort);

    connect(ui->loadButton, SIGNAL(clicked()), this, SLOT (loadFromFile()));
    connect(ui->saveButton, SIGNAL(clicked()), this, SLOT (saveToFile()));

}


MainWindow::~MainWindow()
{
    delete ui;
    delete scene;
}
void MainWindow::updatePorts(){
    //zmeni updatne list available ports
    availablePorts.clear();
    availablePorts.append(defaultPort);

    for(auto &i: inputBoxesList){
        availablePorts.append(QString::number(i->id)+QString("-out"));

    }
    for(auto &i: operationBoxesList){
        availablePorts.append(QString::number(i->id)+QString("-in1"));
        availablePorts.append(QString::number(i->id)+QString("-in2"));
        availablePorts.append(QString::number(i->id)+QString("-out"));
    }
    for(auto &i: outputBoxesList){
         availablePorts.append(QString::number(i->id)+QString("-in1"));
    }
    //projde listy a naplni hodnotama
    for(auto &i: inputBoxesList){
        updateInputBoxPort(i);

    }
    for(auto &i: operationBoxesList){
        updateOperationBoxPort(i,"in1");
        updateOperationBoxPort(i,"in2");
        updateOperationBoxPort(i,"out");
    }
    for(auto &i: outputBoxesList){
        updateOutputBoxPort(i);
    }
}

void MainWindow::updateInputBoxPort(auto &i){

    i->comboBoxOutput->blockSignals(true);
    QString currVal;
    QString currBoxId = QString::number(i->id);
    QList<QString> tmpList;
    int temp_index = 0;
     //ulozi selected, vymaze puvodni stav, vytvori potrebny regex
     currVal = i->comboBoxOutput->currentText();
     i->comboBoxOutput->clear();
        QRegExp regEx(".{1,4}-out");
        //do input portu muzou prijit jen output porty a naopak takze osetreni
        for(auto &list: availablePorts){
            if (!regEx.exactMatch(list)){
                tmpList.append(list);
            }
        }
        //naplni novyma hodnotama, smaze self porty a da zpatky selected
      i->comboBoxOutput->addItems(tmpList);
      //smaze z listu self porty
      //da zpatky ten selected
      temp_index = i->comboBoxOutput->findText(currVal);
      //osetreni 2x stejne hodnoty pri vkladani selected
      if(temp_index >= 0){
        i->comboBoxOutput->setCurrentIndex(temp_index);
      }
      else{
           i->comboBoxOutput->setCurrentIndex(0);
      }
       tmpList.clear();
       i->comboBoxOutput->blockSignals(false);

}

void MainWindow::updateOperationBoxPort(auto &i,QString port){

    i->comboBoxInput1->blockSignals(true);
    i->comboBoxInput2->blockSignals(true);
    i->comboBoxOutput->blockSignals(true);

    QString currVal;
    QString specRegExp;
    QString currBoxId = QString::number(i->id);
    QList<QString> tmpList;
    int temp_index = 0;

        //ulozi selected, vymaze puvodni stav, vytvori potrebny regex
        if (port == "in1"){
            currVal = i->comboBoxInput1->currentText();
            i->comboBoxInput1->clear();
            specRegExp = ".{1,4}-in.{1}";
        }else if(port == "in2"){
            currVal = i->comboBoxInput2->currentText();
            i->comboBoxInput2->clear();
            specRegExp = ".{1,4}-in.{1}";
        }else{
            currVal = i->comboBoxOutput->currentText();
            i->comboBoxOutput->clear();
            specRegExp = ".{1,4}-out";
        }
        QRegExp regEx(specRegExp);
        //do input portu muzou prijit jen output porty a naopak takze osetreni
        for(auto &list: availablePorts){
            if (!regEx.exactMatch(list)){
                tmpList.append(list);
            }
        }
        //naplni novyma hodnotama, smaze self porty a da zpatky selected
        if (port == "in1"){
            i->comboBoxInput1->addItems(tmpList);
            //smaze z listu self porty
            i->comboBoxInput1->removeItem(i->comboBoxInput1->findText(currBoxId+QString("-out")));
            //da zpatky ten selected
            temp_index = i->comboBoxInput1->findText(currVal);
            //osetreni 2x stejne hodnoty pri vkladani selected
            if(temp_index >= 0){
                i->comboBoxInput1->setCurrentIndex(temp_index);
            }
            else{
                i->comboBoxInput1->setCurrentIndex(0);
            }
        }else if(port == "in2"){
            i->comboBoxInput2->addItems(tmpList);
            //smaze z listu self porty
            i->comboBoxInput2->removeItem(i->comboBoxInput2->findText(currBoxId+QString("-out")));
            //da zpatky ten selected
            temp_index = i->comboBoxInput2->findText(currVal);
            //osetreni 2x stejne hodnoty pri vkladani selected
            if(temp_index >= 0){
                i->comboBoxInput2->setCurrentIndex(temp_index);
            }
            else{
                i->comboBoxInput2->setCurrentIndex(0);
            }
        }else{
             i->comboBoxOutput->addItems(tmpList);
             //smaze z listu self porty
             i->comboBoxOutput->removeItem(i->comboBoxOutput->findText(currBoxId+QString("-in1")));
             i->comboBoxOutput->removeItem(i->comboBoxOutput->findText(currBoxId+QString("-in2")));
             //da zpatky ten selected
             temp_index = i->comboBoxOutput->findText(currVal);
             //osetreni 2x stejne hodnoty pri vkladani selected
             if(temp_index >= 0){
                 i->comboBoxOutput->setCurrentIndex(temp_index);
             }
             else{
                 i->comboBoxOutput->setCurrentIndex(0);
             }
        }

        tmpList.clear();

        i->comboBoxInput1->blockSignals(false);
        i->comboBoxInput2->blockSignals(false);
        i->comboBoxOutput->blockSignals(false);
}

void MainWindow::updateOutputBoxPort(auto &i){

    i->comboBoxInput1->blockSignals(true);
    QString currVal;
    QString currBoxId = QString::number(i->id);
    QList<QString> tmpList;
    int temp_index = 0;

        //ulozi selected, vymaze puvodni stav, vytvori potrebny regex

        currVal = i->comboBoxInput1->currentText();
        i->comboBoxInput1->clear();
        QRegExp regEx(".{1,4}-in.{1}");
        //do input portu muzou prijit jen output porty a naopak takze osetreni
        for(auto &list: availablePorts){
            if (!regEx.exactMatch(list)){
                tmpList.append(list);
            }
        }
        //naplni novyma hodnotama, smaze self porty a da zpatky selected
        i->comboBoxInput1->addItems(tmpList);
        //smaze z listu self porty
        i->comboBoxInput1->removeItem(i->comboBoxInput1->findText(currBoxId+QString("-out")));
        //da zpatky ten selected
        temp_index = i->comboBoxInput1->findText(currVal);
        //osetreni 2x stejne hodnoty pri vkladani selected
        if(temp_index >= 0){
            i->comboBoxInput1->setCurrentIndex(temp_index);
        }
        else{
            i->comboBoxInput1->setCurrentIndex(0);
        }


    tmpList.clear();
    i->comboBoxInput1->blockSignals(false);
}

void MainWindow::on_plusBoxButton_clicked()
{

     createSpecificOperationBox("+");

}

void MainWindow::on_inputButton_clicked()
{
    InputBox *temp = new InputBox(&scene, inputBoxesList);
    temp->id = id;
    temp->labelName->setText(QString("obj ")+QString::number(id));
    temp->comboBoxOutput->setCurrentText(defaultPort);
    inputBoxesList.append(temp);

    id++;
    updatePorts();

    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));
    connect(temp, SIGNAL (sigOnChangeOut(QString, QString)), this, SLOT(onChangeOutMain(QString, QString)));
    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));

}

void MainWindow::drawLines(){

    QBrush blueBrush(Qt::blue);
    QPen Pen(Qt::black);

    Pen.setWidth(3);

    if(!linesList.empty()){
     for (auto &i: linesList){

        int temp2 = linesList.indexOf(i);
        (linesList).removeAt(temp2);
        delete i;

     }

    }


    for(auto &i: operationBoxesList){
        QString start_in1_text = i->comboBoxInput1->currentText();
        QString start_in2_text = i->comboBoxInput2->currentText();
        QString start_out_text = i->comboBoxOutput->currentText();

        int start_in1_x = i->mainItem->pos().x();
        int start_in1_y = i->mainItem->pos().y()+58;
        int start_in2_x = i->mainItem->pos().x();
        int start_in2_y = i->mainItem->pos().y()+118;
        int start_out_x = i->mainItem->pos().x()+190;
        int start_out_y = i->mainItem->pos().y()+88;

       for(auto &j: operationBoxesList){
           QStringList start_in1_text_split = start_in1_text.split('-');
           QStringList start_in2_text_split = start_in2_text.split('-');
           QStringList start_out_text_split = start_out_text.split('-');

           QString temp_label_text = "<span style=\"background-color:white;\">Value right: "+QString::number(i->resultValue)+", Value left:"+QString::number(j->resultValue) +"</span";

           if (QString::number(j->id) == start_in1_text_split[0]){

                int end_x = j->mainItem->pos().x()+190;
                int end_y = j->mainItem->pos().y()+88;
                QGraphicsLineItem *line = (*scene).addLine(start_in1_x, start_in1_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);
                linesList.append(line);

           }

           if (QString::number(j->id) == start_in2_text_split[0]){

                int end_x = j->mainItem->pos().x()+190;
                int end_y = j->mainItem->pos().y()+88;
                QGraphicsLineItem *line = (*scene).addLine(start_in2_x, start_in2_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);

           }
           if (QString::number(j->id) == start_out_text_split[0]){
                int end_x;
                int end_y;

               if(start_out_text_split[1] == "in1"){
                    end_x = j->mainItem->pos().x();
                    end_y = j->mainItem->pos().y() + 58;
               }
               if(start_out_text_split[1] == "in2"){
                    end_x = j->mainItem->pos().x();
                    end_y = j->mainItem->pos().y()+118;
               }

                QGraphicsLineItem *line = (*scene).addLine(start_out_x, start_out_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);
           }
        }

       for(auto &j: inputBoxesList){
           QStringList start_in1_text_split = start_in1_text.split('-');
           QStringList start_in2_text_split = start_in2_text.split('-');

           QString temp_label_text = "<span style=\"background-color:white;\">Value right: "+QString::number(i->resultValue)+", Value left:"+QString::number(j->resultValue) +"</span";

           if (QString::number(j->id) == start_in1_text_split[0]){

                int end_x = j->mainItem->pos().x()+190;
                int end_y = j->mainItem->pos().y()+43;
                QGraphicsLineItem *line = (*scene).addLine(start_in1_x, start_in1_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);
           }

           if (QString::number(j->id) == start_in2_text_split[0]){

                int end_x = j->mainItem->pos().x()+190;
                int end_y = j->mainItem->pos().y()+43;
                QGraphicsLineItem *line = (*scene).addLine(start_in2_x, start_in2_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);
           }
       }

       for(auto &j: outputBoxesList){
           QStringList start_out_text_split = start_out_text.split('-');
           QString temp_label_text = "<span style=\"background-color:white;\">Value right: "+QString::number(i->resultValue)+", Value left:"+QString::number(j->resultValue) +"</span";

           if (QString::number(j->id) == start_out_text_split[0]){

                int end_x = j->mainItem->pos().x();
                int end_y = j->mainItem->pos().y()+43;
                QGraphicsLineItem *line = (*scene).addLine(start_out_x, start_out_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);

           }
       }
    }

    for(auto &i: inputBoxesList){
        QString start_out_text = i->comboBoxOutput->currentText();

        int start_out_x = i->mainItem->pos().x()+190;
        int start_out_y = i->mainItem->pos().y()+43;

       for(auto &j: outputBoxesList){
           QStringList start_out_text_split = start_out_text.split('-');
           QString temp_label_text = "<span style=\"background-color:white;\">Value right: "+QString::number(i->resultValue)+", Value left:"+QString::number(j->resultValue) +"</span";

           if (QString::number(j->id) == start_out_text_split[0]){

                int end_x = j->mainItem->pos().x();
                int end_y = j->mainItem->pos().y()+43;
                QGraphicsLineItem *line = (*scene).addLine(start_out_x, start_out_y, end_x, end_y,Pen);
                line->setToolTip(temp_label_text);

                linesList.append(line);

           }
       }
    }

}

void MainWindow::onChangeIn1Main(QString in_port, QString out_port){

    QStringList in_temp = in_port.split('-');
    QStringList out_temp = out_port.split('-');

    for(auto &i: operationBoxesList){

        if (QString::number(i->id) == out_temp[0]){

            int temp_index = i->comboBoxOutput->findText(in_port);
            //osetreni 2x stejne hodnoty pri vkladani selected
            if(temp_index >= 0){
                i->comboBoxOutput->setCurrentIndex(temp_index);
            }
            else{
                i->comboBoxOutput->setCurrentIndex(0);
            }
        }
    }

    for(auto &i: inputBoxesList){
        if (QString::number(i->id) == out_temp[0]){

            int temp_index = i->comboBoxOutput->findText(in_port);
            //osetreni 2x stejne hodnoty pri vkladani selected
            if(temp_index >= 0){
                i->comboBoxOutput->setCurrentIndex(temp_index);
            }
            else{
                i->comboBoxOutput->setCurrentIndex(0);
            }
        }
    }


    drawLines();

}

void MainWindow::onChangeOutMain(QString in_port, QString out_port){

    QStringList in_temp = in_port.split('-');
    QStringList out_temp = out_port.split('-');

    // OperationBox
    for(auto &i: operationBoxesList){
        if (QString::number(i->id) == in_temp[0]){

            if(in_temp[1] == "in1"){
                int temp_index = i->comboBoxInput1->findText(out_port);
                //osetreni 2x stejne hodnoty pri vkladani selected
                if(temp_index >= 0){
                    i->comboBoxInput1->setCurrentIndex(temp_index);
                }
                else{
                    i->comboBoxInput1->setCurrentIndex(0);
                }
            }
            else if (in_temp[1] == "in2"){
                int temp_index = i->comboBoxInput2->findText(out_port);
                //osetreni 2x stejne hodnoty pri vkladani selected
                if(temp_index >= 0){
                    i->comboBoxInput2->setCurrentIndex(temp_index);
                }
                else{
                    i->comboBoxInput2->setCurrentIndex(0);
                }
            }
        }
    }
    //InputBox

    for(auto &i: outputBoxesList){
        if (QString::number(i->id) == in_temp[0]){

            if(in_temp[1] == "in1"){
                int temp_index = i->comboBoxInput1->findText(out_port);
                //osetreni 2x stejne hodnoty pri vkladani selected
                if(temp_index >= 0){
                    i->comboBoxInput1->setCurrentIndex(temp_index);
                }
                else{
                    i->comboBoxInput1->setCurrentIndex(0);
                }
            }
        }
    }



    drawLines();
}

void MainWindow::on_outputButton_clicked()
{

    OutputBox *temp = new OutputBox(&scene, outputBoxesList);
    temp->id = id;
    temp->labelName->setText(QString("obj ")+QString::number(id));     
    temp->comboBoxInput1->setCurrentText(defaultPort);

    outputBoxesList.append(temp);
    id++;
    updatePorts();

    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));
    connect(temp, SIGNAL (sigOnChangeIn1(QString, QString)), this, SLOT(onChangeIn1Main(QString, QString)));
    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));

}

void MainWindow::on_runButton_clicked()
{
    QList<OperationBox *> tmpList;
    if (!check()){
            return;
        }
    for(auto &i: inputBoxesList){
        i->mainItem->setBrush(Qt::red);
        i->mainItem->update(0,20,200,125);
        this->ui->graphicsView->viewport()->repaint();
        i->calculate(operationBoxesList,outputBoxesList);
        QThread::msleep(1000);
        i->mainItem->setBrush(Qt::yellow);
        i->mainItem->update(0,20,200,125);
        this->ui->graphicsView->viewport()->repaint();

    }
    while (tmpList.size() != operationBoxesList.size()){
        for(auto &i: operationBoxesList){
            if (i->calculate(operationBoxesList,outputBoxesList)){
                if (!tmpList.contains(i)){

                    i->mainItem->setBrush(Qt::red);
                    i->mainItem->update(0,20,200,125);
                    this->ui->graphicsView->viewport()->repaint();
                    tmpList.append(i);
                    QThread::msleep(1000);
                    i->mainItem->setBrush(Qt::blue);
                    i->mainItem->update(0,20,200,125);
                    this->ui->graphicsView->viewport()->repaint();
                }
            }
        }
    }
    for(auto &i: outputBoxesList){
        i->mainItem->setBrush(Qt::red);
        i->mainItem->update(0,20,200,125);
        this->ui->graphicsView->viewport()->repaint();
        i->calculate();
        QThread::msleep(1000);
        i->mainItem->setBrush(Qt::green);
        i->mainItem->update(0,20,200,125);
        this->ui->graphicsView->viewport()->repaint();
    }
    drawLines();
}

void MainWindow::on_minusBoxButton_clicked()
{
    createSpecificOperationBox("-");
}

void MainWindow::createSpecificOperationBox(QString type){

    OperationBox *temp = new OperationBox(&scene, operationBoxesList);
    temp->id = id;
    temp->type = type;
    temp->labelType->setText(type);
    temp->labelName->setText(QString("obj ")+QString::number(id));

    temp->comboBoxInput1->setCurrentText(defaultPort);
    temp->comboBoxInput2->setCurrentText(defaultPort);
    temp->comboBoxOutput->setCurrentText(defaultPort);

    operationBoxesList.append(temp);
    id++;
    updatePorts();

    connect(temp, SIGNAL (sigOnChangeIn1(QString, QString)), this, SLOT(onChangeIn1Main(QString, QString)));
    connect(temp, SIGNAL (sigOnChangeOut(QString, QString)), this, SLOT(onChangeOutMain(QString, QString)));
    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));
    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));

}

void MainWindow::on_multiBoxButton_clicked()
{
    createSpecificOperationBox("*");
}

void MainWindow::on_divideBoxButton_clicked()
{
    createSpecificOperationBox("/");
}

void MainWindow::on_labelHover(){

    drawLines();
}

bool MainWindow::check(){
    QMessageBox msgBox;
    QString message = "";
    bool notUsedAllPorts = false;
    bool usedMoreThanOnce = false;
    QList<QString> tmpPortList;

    //pro inputboxes
     for(auto &i: inputBoxesList){
         if (!tmpPortList.contains(i->comboBoxOutput->currentText())){
             tmpPortList.append(i->comboBoxOutput->currentText());
         }else{
             usedMoreThanOnce = true;
             message.append(i->comboBoxOutput->currentText());
             message.append("<br>");
         }
         if (i->comboBoxOutput->currentText() == defaultPort){
             notUsedAllPorts = true;
         }
    }
     for(auto &i: operationBoxesList){
         //pro input1
         if (!tmpPortList.contains(i->comboBoxInput1->currentText())){
             tmpPortList.append(i->comboBoxInput1->currentText());
         }else{
             usedMoreThanOnce = true;
             message.append(i->comboBoxInput1->currentText());
             message.append("<br>");
         }
         if (i->comboBoxOutput->currentText() == defaultPort){
             notUsedAllPorts = true;
         }
        //pro input2
         if (!tmpPortList.contains(i->comboBoxInput2->currentText())){
             tmpPortList.append(i->comboBoxInput2->currentText());
         }else{
             usedMoreThanOnce = true;
             message.append(i->comboBoxInput2->currentText());
             message.append("<br>");
         }
         if (i->comboBoxInput2->currentText() == defaultPort){
             notUsedAllPorts = true;
         }
        //pro output
         if (!tmpPortList.contains(i->comboBoxOutput->currentText())){
             tmpPortList.append(i->comboBoxOutput->currentText());
         }else{
             usedMoreThanOnce = true;
             message.append(i->comboBoxOutput->currentText());
             message.append("<br>");
         }
         if (i->comboBoxOutput->currentText() == defaultPort){
             notUsedAllPorts = true;
         }
    }
     //pro ouput boxes
     for(auto &i: outputBoxesList){
         if (!tmpPortList.contains(i->comboBoxInput1->currentText())){
             tmpPortList.append(i->comboBoxInput1->currentText());
         }else{
             usedMoreThanOnce = true;
             message.append(i->comboBoxInput1->currentText());
             message.append("<br>");
         }
         if (i->comboBoxInput1->currentText() == defaultPort){
             notUsedAllPorts = true;
         }
    }

     if (notUsedAllPorts){
         msgBox.setText("Některé porty nejsou vyplněny, prosím vyplňte je\n");
         msgBox.setInformativeText(message);
         msgBox.exec();
         return false;
     }
     if (usedMoreThanOnce){
         msgBox.setText("Tyto porty jsou předávány na více míst\n");
         msgBox.setInformativeText(message);
         msgBox.exec();
         return false;
     }

    return true;

}

void MainWindow::on_runStepButton_clicked()
{
    //id na 0
    stepId = 0;
    orderStep.clear();
    stepByPrep("repaint");
    //nacist v jakym poradi to probehne
    stepByPrep("order");
    //uklidit si
    stepByPrep("clean");
    stepId = -1;

}

void MainWindow::stepByPrep(QString type){
    QList<OperationBox *> tmpList;
    if (!check()){
            return;
        }
    if (type == "repaint"){
        for(auto &i: inputBoxesList){
            i->mainItem->setBrush(Qt::yellow);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
        }
    }else{
        for(auto &i: inputBoxesList){
            i->calculate(operationBoxesList,outputBoxesList);
            if (type == "clean"){
                i->resultValue = 0;
                i->outputPort.first = "nonValid";
                i->outputPort.second = 0;
            }
            if (type == "order"){
                orderStep.push_back(i->id);
            }
        }
    }
    if (type == "order"){
        while (tmpList.size() != operationBoxesList.size()){
            for(auto &i: operationBoxesList){
                if (i->calculate(operationBoxesList,outputBoxesList)){
                    if (!tmpList.contains(i)){
                        tmpList.append(i);
                        orderStep.push_back(i->id);
                        }
                    }
                }
            }
     }

    if (type == "clean"){
        for(auto &i: operationBoxesList){
            i->resultValue = 0;
            i->inputPort1.first = "nonValid";
            i->inputPort1.second = 0;
            i->inputPort2.first = "nonValid";
            i->inputPort2.second = 0;
            i->outputPort.first = "nonValid";
            i->outputPort.second = 0;
        }
     }
    if (type == "repaint"){
        for(auto &i: operationBoxesList){
            i->mainItem->setBrush(Qt::blue);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
        }
    }
    if (type == "repaint"){
        for(auto &i: outputBoxesList){
            i->mainItem->setBrush(Qt::green);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
        }
    }else{
        for(auto &i: outputBoxesList){
            i->calculate();
            if (type == "clean"){
                i->resultValue = 0;
                i->inputPort1.first = "nonValid";
                i->inputPort1.second = 0;
                i->result->setText("0");
            }
            if (type == "order"){
                orderStep.push_back(i->id);
            }
        }
    }

}

void MainWindow::on_nextStepButton_clicked()
{
    if (stepId < orderStep.size()-1){
        stepId++;
    }

    //vratit barvu puvodnimu
        //stepId--;
        //najdi ho a prebarvi ho zpatky
        for(auto &i: inputBoxesList){
            if (stepId != 0){
                if (i->id == orderStep.at(stepId-1)){
                    i->mainItem->setBrush(Qt::yellow);
                    i->mainItem->update(0,20,200,125);
                    this->ui->graphicsView->viewport()->repaint();
                    break;
                }
            }
        }
        for(auto &i: operationBoxesList){
            if (stepId != 0){
                if (i->id == orderStep.at(stepId-1)){
                    i->mainItem->setBrush(Qt::blue);
                    i->mainItem->update(0,20,200,125);
                    this->ui->graphicsView->viewport()->repaint();
                    break;
                }
            }
        }
        for(auto &i: outputBoxesList){
            if (stepId != 0){
                if (i->id == orderStep.at(stepId-1)){
                    i->mainItem->setBrush(Qt::green);
                    i->mainItem->update(0,20,200,125);
                    this->ui->graphicsView->viewport()->repaint();
                    break;
                }
            }
        }

    //presunout se na novy
    if (stepId < orderStep.size()-1){
        //stepId = orderStep.at(stepId+1);

    }

        //najdi ho
        //zmen barvu
        //vypocitej
    for(auto &i: inputBoxesList){
        if (i->id == orderStep.at(stepId)){
            i->calculate(operationBoxesList,outputBoxesList);
            i->mainItem->setBrush(Qt::red);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
            break;
        }
    }
    for(auto &i: operationBoxesList){
        if (i->id == orderStep.at(stepId)){
            i->calculate(operationBoxesList,outputBoxesList);
            i->mainItem->setBrush(Qt::red);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
            break;
        }
    }
    for(auto &i: outputBoxesList){
        if (i->id == orderStep.at(stepId)){
            i->calculate();
            i->mainItem->setBrush(Qt::red);
            i->mainItem->update(0,20,200,125);
            this->ui->graphicsView->viewport()->repaint();
            break;
        }
    }
    drawLines();
}

void MainWindow::loadFromFile(){

     QString fileName = QFileDialog::getOpenFileName(this,tr("Load block scheme"), "",tr("Block Scheme (*.bicp);;All Files (*)"));

     if (fileName.isEmpty())
         return;
     else {

         QFile file(fileName);

         if (!file.open(QFile::ReadOnly)) {
             QMessageBox::information(this, tr("Unable to open file"),
                 file.errorString());
             return;
         }
         //smazat co tam bylo
         for (auto &i: inputBoxesList){
             delete i->mainItem;
         }
         inputBoxesList.clear();
         for (auto &i: operationBoxesList){
             delete i->mainItem;
         }
         operationBoxesList.clear();
         for (auto &i: outputBoxesList){
             delete i->mainItem;
         }
         outputBoxesList.clear();
         for (auto &i: linesList){
             int temp2 = linesList.indexOf(i);
             (linesList).removeAt(temp2);
             delete i;
         }
         linesList.clear();
         availablePorts.clear();

         QTextStream in(&file);

         int tempId = 0;
         while (!in.atEnd()){
                QString line = in.readLine();
                QStringList tmpList = line.split(';');

                if (tmpList.at(0) == "in"){

                    InputBox *temp = new InputBox(&scene, inputBoxesList);
                    temp->id = tmpList.at(1).toInt();
                    if (temp->id > tempId){
                        tempId = temp->id;
                    }
                    temp->labelName->setText(QString("obj ")+QString::number(temp->id));

                    temp->mainItem->setPos((tmpList.at(2)).toInt(),(tmpList.at(3)).toInt());
                    inputBoxesList.append(temp);
                    temp->comboBoxOutput->addItem(tmpList.at(6));
                    temp->comboBoxOutput->setCurrentText(tmpList.at(6));
                    temp->inputSpinBox->setValue(tmpList.at(7).toDouble());

                    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));
                    connect(temp, SIGNAL (sigOnChangeOut(QString, QString)), this, SLOT(onChangeOutMain(QString, QString)));
                    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));


                }else if (tmpList.at(0) == "out"){

                    OutputBox *temp = new OutputBox(&scene, outputBoxesList);
                    temp->id = tmpList.at(1).toInt();
                    if (temp->id > tempId){
                        tempId = temp->id;
                    }
                    temp->labelName->setText(QString("obj ")+QString::number(temp->id));

                    temp->mainItem->setPos((tmpList.at(2)).toInt(),(tmpList.at(3)).toInt());
                    outputBoxesList.append(temp);

                    temp->comboBoxInput1->addItem(tmpList.at(4));
                    temp->comboBoxInput1->setCurrentText(tmpList.at(4));
                    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));
                    connect(temp, SIGNAL (sigOnChangeIn1(QString, QString)), this, SLOT(onChangeIn1Main(QString, QString)));
                    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));


                }else{

                    OperationBox *temp = new OperationBox(&scene, operationBoxesList);
                    temp->id = tmpList.at(1).toInt();
                    if (temp->id > tempId){
                        tempId = temp->id;
                    }
                    temp->type = tmpList.at(0);
                    temp->labelType->setText(temp->type);
                    temp->labelName->setText(QString("obj ")+QString::number(temp->id));

                    temp->comboBoxInput1->addItem(tmpList.at(4));
                    temp->comboBoxInput2->addItem(tmpList.at(5));
                    temp->comboBoxOutput->addItem(tmpList.at(6));

                    temp->comboBoxInput1->setCurrentText(tmpList.at(4));
                    temp->comboBoxInput2->setCurrentText(tmpList.at(5));
                    temp->comboBoxOutput->setCurrentText(tmpList.at(6));
                    temp->mainItem->setPos((tmpList.at(2)).toInt(),(tmpList.at(3)).toInt());
                    operationBoxesList.append(temp);

                    connect(temp, SIGNAL (sigOnChangeIn1(QString, QString)), this, SLOT(onChangeIn1Main(QString, QString)));
                    connect(temp, SIGNAL (sigOnChangeOut(QString, QString)), this, SLOT(onChangeOutMain(QString, QString)));
                    connect(temp, SIGNAL(box_deleted()),this,SLOT(updatePorts()));
                    connect(temp->labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));

                }

             }
         updatePorts();
         this->ui->graphicsView->viewport()->repaint();
         drawLines();
         tempId++;
         id = tempId;
         file.close();

     }

}

void MainWindow::saveToFile(){

    QString fileName = QFileDialog::getSaveFileName(this,tr("Save block scheme"), "",tr("Block Scheme (*.bicp);;All Files (*)"));

    if (fileName.isEmpty())
        return;
    else {
        QFile file(fileName);
        if (!file.open(QFile::WriteOnly)) {
            QMessageBox::information(this, tr("Unable to open file"),
                file.errorString());
            return;
        }

        QTextStream out(&file);
        for(auto &i: operationBoxesList){
            QString temp_line = "";
            temp_line = i->type + ";" +
                        QString::number(i->id) + ";" +
                        QString::number(i->mainItem->pos().x()) + ";" +
                        QString::number(i->mainItem->pos().y()) + ";" +
                        i->comboBoxInput1->currentText() + ";" +
                        i->comboBoxInput2->currentText() + ";" +
                        i->comboBoxOutput->currentText() + ";" +
                        "None";
            out << temp_line <<endl;

         }
        for(auto &i: inputBoxesList){
            QString temp_line = "";
            temp_line = "in;" +
                        QString::number(i->id) + ";" +
                        QString::number(i->mainItem->pos().x()) + ";" +
                        QString::number(i->mainItem->pos().y()) + ";" +
                        "None;" +
                        "None;" +
                        i->comboBoxOutput->currentText() + ";" +
                        QString::number(i->inputSpinBox->value());
            out << temp_line <<endl;
        }
        for(auto &i: outputBoxesList){
            QString temp_line = "";
            temp_line = "out;" +
                        QString::number(i->id) + ";" +
                        QString::number(i->mainItem->pos().x()) + ";" +
                        QString::number(i->mainItem->pos().y()) + ";" +
                        i->comboBoxInput1->currentText() + ";" +
                        "None;" +
                        "None;" +
                        "None";
            out << temp_line <<endl;

         }


    }

}

OperationBox::OperationBox(auto *scene,QList<OperationBox*> &boxesList){

    inputPort1.first = "nonValid";
    inputPort1.second = 0.0;
    inputPort2.first = "nonValid";
    inputPort2.second = 0.0;
    outputPort.first = "nonValid";
    outputPort.second = 0.0;
    resultValue = 0;

    boxesListTemp = &boxesList;

    QBrush blueBrush(Qt::blue);
    QPen Pen(Qt::black);
    mainItem = (*scene)->addRect(0,20,200,125,Pen,blueBrush);
    mainItem->setFlags(QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable | QGraphicsItem::ItemSendsGeometryChanges);
    mainItem->setData(0,inputPort1.second);
    comboBoxInput1 = new QComboBox();
    comboBoxInput2 = new QComboBox();
    comboBoxOutput = new QComboBox();
    labelType = new QLabel();
    labelName = new QLabel();



    deleteButton = new QPushButton();
    deleteButton->setText("Delete");


    comboBoxInput1->setFixedHeight(25);
    comboBoxInput1->setFixedWidth(75);
    comboBoxInput2->setFixedHeight(25);
    comboBoxInput2->setFixedWidth(75);
    comboBoxOutput->setFixedHeight(25);
    comboBoxOutput->setFixedWidth(75);

    labelType->setFixedHeight(25);
    labelType->setFixedWidth(25);
    labelName->setFixedHeight(25);
    labelName->setFixedWidth(100);

    QFont font = labelType->font();
    font.setPointSize(20);
    font.setBold(true);
    labelType->setFont(font);
    labelType->setAlignment(Qt::AlignCenter);
    labelType->setAutoFillBackground(false);
    labelType->setStyleSheet("background:transparent");

    labelName->setFont(font);
    labelName->setAutoFillBackground(false);
    labelName->setStyleSheet("background:transparent");


    labelInput1 = new QLabel();
    labelInput2 = new QLabel();
    labelOutput = new QLabel();
    QFont font2 = labelInput1->font();
    font2.setPointSize(12);
    labelInput1->setFont(font2);
    labelInput1->setAutoFillBackground(false);
    labelInput1->setStyleSheet("background:transparent");
    labelInput1->setText("Input1:");

    labelInput2->setFont(font2);
    labelInput2->setAutoFillBackground(false);
    labelInput2->setStyleSheet("background:transparent");
    labelInput2->setText("Input2:");

    labelOutput->setFont(font2);
    labelOutput->setAutoFillBackground(false);
    labelOutput->setStyleSheet("background:transparent");
    labelOutput->setText("Output:");
    QGraphicsProxyWidget* labelInput1Proxy = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelInput2Proxy = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelOutputProxy = new QGraphicsProxyWidget(mainItem);
    labelInput1Proxy->setWidget(labelInput1);
    labelInput2Proxy->setWidget(labelInput2);
    labelOutputProxy->setWidget(labelOutput);

    QGraphicsProxyWidget* comboProxyInput1 = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* comboProxyInput2 = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* comboProxyOutput = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelTypeProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelNameProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* deleteProxyButton = new QGraphicsProxyWidget(mainItem);




    comboProxyInput1->setWidget(comboBoxInput1);
    comboProxyInput2->setWidget(comboBoxInput2);
    comboProxyOutput->setWidget(comboBoxOutput);
    labelTypeProxyName->setWidget(labelType);
    labelNameProxyName->setWidget(labelName);
    deleteProxyButton->setWidget(deleteButton);



    labelInput1Proxy->setPos(10,20);
    comboProxyInput1->setPos(10, 45);
    labelInput2Proxy->setPos(10,85);
    comboProxyInput2->setPos(10, 105);
    labelOutputProxy->setPos(115,56);
    comboProxyOutput->setPos(115,76 );
    labelTypeProxyName->setPos(150,35);
    labelNameProxyName->setPos(0,-5);
    deleteProxyButton->setPos(120,145);

    // HOVER LABEL
    labelHover = new CustomLabel();
    labelHover->setFixedHeight(125);
    labelHover->setFixedWidth(200);
    labelHover->setStyleSheet("background:transparent");
    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);
    QGraphicsProxyWidget* labelHoverProxy = new QGraphicsProxyWidget(mainItem);
    labelHoverProxy->setWidget(labelHover);
    labelHoverProxy->setPos(0,20);

    connect(comboBoxInput1, SIGNAL (currentIndexChanged(QString)), this, SLOT(onChangeIn1(QString)));
    connect(comboBoxInput2, SIGNAL (currentIndexChanged(QString)), this, SLOT(onChangeIn2(QString)));
    connect(comboBoxOutput, SIGNAL (currentIndexChanged(QString)), this, SLOT(onChangeOut(QString)));
    connect(deleteButton, SIGNAL (clicked()), this, SLOT (on_deleteButton_clicked()));
    connect(labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));

}

OperationBox::~OperationBox(){
    delete labelName;
    delete mainItem;
    delete deleteButton;
    delete labelHover;

    delete labelInput1;
    delete labelInput2;
    delete labelOutput;

    delete boxesListTemp;
    delete labelType;
    delete comboBoxInput1;
    delete comboBoxInput2;
    delete comboBoxOutput;

}

bool OperationBox::calculate(auto operationBoxesList, auto outputBoxesList){
    QString targetObj;
    QString targetPort;
    bool found = false;
    if (inputPort1.first == "valid" && inputPort2.first == "valid"){
        if (type == "+"){
            resultValue = inputPort1.second + inputPort2.second;

        }
        if (type == "-"){
            resultValue = inputPort1.second - inputPort2.second;

        }
        if (type == "*"){
            resultValue = inputPort1.second * inputPort2.second;

        }
        if (type == "/"){
            resultValue = inputPort1.second / inputPort2.second;

        }

        //zjistim komu a kam
        targetObj = comboBoxOutput->currentText().section('-',0,0);
        targetPort = comboBoxOutput->currentText().section('-',1,1);

        for(auto &i: operationBoxesList){
            if (QString::number(i->id) == targetObj){
                found = true;
                if (targetPort == "in1"){
                    i->inputPort1.first = "valid";
                    i->inputPort1.second = resultValue;
                }
                if (targetPort == "in2"){
                    i->inputPort2.first = "valid";
                    i->inputPort2.second = resultValue;
                }
                break;
            }
        }
        //pokud jsem nenasel v operation box
        if (!found){
            for(auto &i: outputBoxesList){
                if (QString::number(i->id) == targetObj){
                    i->inputPort1.first = "valid";
                    i->inputPort1.second = resultValue;
                    break;
                }
            }
        }
        return true;
   }
    return false;
}

void OperationBox::on_deleteButton_clicked(){
    QObject *temp = sender();

    delete mainItem;
    int temp2 = ((*boxesListTemp).indexOf(this));
    (*boxesListTemp).removeAt(temp2);
    emit box_deleted();

}
void OperationBox::onChangeIn1(QString port_name){

    QString in_port = QString::number(id) + "-in1";
    QString out_port = port_name ;
    emit sigOnChangeIn1(in_port, out_port);
}

void OperationBox::onChangeIn2(QString port_name){

    QString in_port = QString::number(id) + "-in2";
    QString out_port = port_name ;
    emit sigOnChangeIn1(in_port, out_port);
}

void OperationBox::onChangeOut(QString port_name){

    QString in_port = port_name;
    QString out_port = QString::number(id) + "-out";
    emit sigOnChangeOut(in_port, out_port);
}

InputBox::InputBox(auto *scene,QList<InputBox*> &boxesList){

    outputPort.first = "nonValid";
    outputPort.second = 0.0;
    resultValue = 0;
    boxesListTemp = &boxesList;

    QBrush blueBrush(Qt::yellow);
    QPen Pen(Qt::black);
    mainItem = (*scene)->addRect(0,20,200,50,Pen,blueBrush);
    mainItem->setFlags(QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);

    comboBoxOutput = new QComboBox();
    labelName = new QLabel();
    inputSpinBox = new QDoubleSpinBox();

    deleteButton = new QPushButton();
    deleteButton->setText("Delete");

    comboBoxOutput->setFixedHeight(25);
    comboBoxOutput->setFixedWidth(75);
    labelName->setFixedHeight(25);
    labelName->setFixedWidth(100);
    inputSpinBox->setFixedHeight(25);
    inputSpinBox->setFixedWidth(75);

    QFont font = labelName->font();
    font.setPointSize(20);
    font.setBold(true);

    labelName->setFont(font);
    labelName->setAutoFillBackground(false);
    labelName->setStyleSheet("background:transparent");



    labelOutput = new QLabel();
    QFont font2 = labelOutput->font();
    font2.setPointSize(12);

    labelOutput->setFont(font2);
    labelOutput->setAutoFillBackground(false);
    labelOutput->setStyleSheet("background:transparent");
    labelOutput->setText("Output:");
    QGraphicsProxyWidget* labelOutputProxy = new QGraphicsProxyWidget(mainItem);
    labelOutputProxy->setWidget(labelOutput);

    QGraphicsProxyWidget* comboProxyOutput = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelNameProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* inputSpinBoxProxy = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* deleteProxyButton = new QGraphicsProxyWidget(mainItem);

    comboProxyOutput->setWidget(comboBoxOutput);
    labelNameProxyName->setWidget(labelName);
    inputSpinBoxProxy->setWidget(inputSpinBox);
    deleteProxyButton->setWidget(deleteButton);

    labelOutputProxy->setPos(115,20);
    comboProxyOutput->setPos(115,40);
    labelNameProxyName->setPos(0,-5);
    inputSpinBoxProxy->setPos(20,30);
    deleteProxyButton->setPos(120,70);

    // HOVER LABEL
    labelHover = new CustomLabel();
    labelHover->setFixedHeight(50);
    labelHover->setFixedWidth(200);
    labelHover->setStyleSheet("background:transparent");
    QGraphicsProxyWidget* labelHoverProxy = new QGraphicsProxyWidget(mainItem);

    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);
    labelHoverProxy->setWidget(labelHover);
    labelHoverProxy->setPos(0,20);

    connect(comboBoxOutput, SIGNAL (currentIndexChanged(QString)), this, SLOT(onChangeOut(QString)));
    connect(deleteButton, SIGNAL (clicked()), this, SLOT (on_deleteButton_clicked()));
    connect(labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));

}

InputBox::~InputBox(){

    delete labelName;
    delete mainItem;
    delete deleteButton;
    delete labelHover;

    delete labelOutput;

    delete boxesListTemp;
    delete comboBoxOutput;
    delete inputSpinBox;
}

void InputBox::on_deleteButton_clicked(){
    QObject *temp = sender();
    delete mainItem;
    int temp2 = ((*boxesListTemp).indexOf(this));
    (*boxesListTemp).removeAt(temp2);
    emit box_deleted();

}


OutputBox::OutputBox(auto *scene,QList<OutputBox*> &boxesList){
    inputPort1.first = "nonValid";
    inputPort1.second = 0.0;
    resultValue = 0;
    boxesListTemp = &boxesList;

    QBrush blueBrush(Qt::green);
    QPen Pen(Qt::black);
    mainItem = (*scene)->addRect(0,20,200,50,Pen,blueBrush);
    mainItem->setFlags(QGraphicsItem::ItemIsMovable | QGraphicsItem::ItemIsSelectable);

    comboBoxInput1 = new QComboBox();
    resultLabel = new QLabel();
    result = new QLineEdit();
    result->setReadOnly(true);
    labelName = new QLabel();
    deleteButton = new QPushButton();
     deleteButton->setText("Delete");

    comboBoxInput1->setFixedHeight(25);
    comboBoxInput1->setFixedWidth(75);
    resultLabel->setFixedHeight(25);
    resultLabel->setFixedWidth(60);
    result->setFixedHeight(25);
    result->setFixedWidth(75);

    labelName->setFixedHeight(25);
    labelName->setFixedWidth(100);

    QFont font = labelName->font();
    font.setPointSize(20);
    font.setBold(true);

    labelName->setFont(font);
    labelName->setAutoFillBackground(false);
    labelName->setStyleSheet("background:transparent");

    resultLabel->setFont(font);
    resultLabel->setAutoFillBackground(false);
    resultLabel->setStyleSheet("background:transparent");


    labelInput1 = new QLabel();

    QFont font2 = labelInput1->font();
    font2.setPointSize(12);
    labelInput1->setFont(font2);
    labelInput1->setAutoFillBackground(false);
    labelInput1->setStyleSheet("background:transparent");
    labelInput1->setText("Input1:");

    QGraphicsProxyWidget* labelInput1Proxy = new QGraphicsProxyWidget(mainItem);

    labelInput1Proxy->setWidget(labelInput1);

    QGraphicsProxyWidget* comboProxyInput = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* labelNameProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* resultLabelProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* resultProxyName = new QGraphicsProxyWidget(mainItem);
    QGraphicsProxyWidget* deleteProxyButton = new QGraphicsProxyWidget(mainItem);

    comboProxyInput->setWidget(comboBoxInput1);
    labelNameProxyName->setWidget(labelName);
    resultLabelProxyName->setWidget(resultLabel);
    resultProxyName->setWidget(result);
    deleteProxyButton->setWidget(deleteButton);

    labelInput1Proxy->setPos(20,20);
    comboProxyInput->setPos(20,40 );
    labelNameProxyName->setPos(0,-5);
    resultLabelProxyName->setPos(70,70);
    resultProxyName->setPos(115,30);
    deleteProxyButton->setPos(120,70);

    // HOVER LABEL
    labelHover = new CustomLabel();
    labelHover->setFixedHeight(50);
    labelHover->setFixedWidth(200);
    labelHover->setStyleSheet("background:transparent");
    QGraphicsProxyWidget* labelHoverProxy = new QGraphicsProxyWidget(mainItem);

    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);

    labelHoverProxy->setWidget(labelHover);
    labelHoverProxy->setPos(0,20);

    connect(comboBoxInput1, SIGNAL (currentIndexChanged(QString)), this, SLOT(onChangeIn1(QString)));
    connect(deleteButton, SIGNAL (clicked()), this, SLOT (on_deleteButton_clicked()));
    connect(labelHover, SIGNAL(label_hover()), this, SLOT(on_labelHover()));

}

OutputBox::~OutputBox(){
    delete labelName;
    delete mainItem;
    delete deleteButton;
    delete labelHover;

    delete labelInput1;

    delete boxesListTemp;
    delete comboBoxInput1;
    delete resultLabel;
    delete result;

}

void OutputBox::on_deleteButton_clicked(){

    QObject *temp = sender();
    delete mainItem;
    int temp2 = ((*boxesListTemp).indexOf(this));
    (*boxesListTemp).removeAt(temp2);
    emit box_deleted();
}

void InputBox::calculate(auto operationBoxesList, auto outputBoxesList){

    QString targetObj;
    QString targetPort;
    bool found = false;
    //zjistim komu a kam
    targetObj = comboBoxOutput->currentText().section('-',0,0);
    targetPort = comboBoxOutput->currentText().section('-',1,1);
    for(auto &i: operationBoxesList){
        if (QString::number(i->id) == targetObj){
            found = true;
            resultValue = double(inputSpinBox->value());
            if (targetPort == "in1"){
                i->inputPort1.first = "valid";
                i->inputPort1.second = resultValue;
            }
            if (targetPort == "in2"){
                i->inputPort2.first = "valid";
                i->inputPort2.second = resultValue;
            }
            break;
        }
    }
    //pokud jsem nenasel v operation box
    if (!found){
        for(auto &i: outputBoxesList){
            if (QString::number(i->id) == targetObj){
                resultValue = double(inputSpinBox->value());
                i->inputPort1.first = "valid";
                i->inputPort1.second = resultValue;
                break;
            }
        }
    }
}

void OutputBox::calculate(){
    if(inputPort1.first == "valid"){
        resultValue = inputPort1.second;
        result->setText(QString::number(resultValue));
    }
}

void InputBox::onChangeOut(QString port_name){
    QString in_port = port_name;
    QString out_port = QString::number(id) + "-out";
    emit sigOnChangeOut(in_port, out_port);
}

void OutputBox::onChangeIn1(QString port_name){

    QString in_port = QString::number(id) + "-in1";
    QString out_port = port_name ;
    emit sigOnChangeIn1(in_port, out_port);
}

void OperationBox::on_labelHover(){

    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);

}

void InputBox::on_labelHover(){
    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);
}

void OutputBox::on_labelHover(){
    QString temp_label_text = "<span style=\"background-color:white;\">Value "+QString::number(resultValue)+"</span";
    labelHover->setToolTip(temp_label_text);
}

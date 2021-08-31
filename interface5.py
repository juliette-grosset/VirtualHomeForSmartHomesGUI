import sys
from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import * 
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore

import os
import json
import datetime

# my modules
import simulation5

sensors = {"kitchen" : {}, "livingroom" : {}, "bathroom" : {}, "bedroom" : {}, "outside" : {}, "entrance" : {}}

activities = {"config" : {}, "activities" : {}}

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Virtual-Home Simulation Interface'
        self.left = 0
        self.top = 0
        self.width = 1800
        self.height = 1000
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()

class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QTabWidget()
        self.tab11 = QWidget()
        self.tab12 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        #self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Generation Sensors file")
        self.tabs.addTab(self.tab2,"Generation Activities file")
        self.tabs.addTab(self.tab3,"Simulation")
        
        # Tab : Generation Sensors file
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(FileBox("sensors"))
        self.tab1.layout.addWidget(AppartmentBox())
        self.tab1.layout.addWidget(GenerationWindow("sensors"))
        self.tab1.setLayout(self.tab1.layout)

        # Tab : Generation activities file
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addWidget(FileBox("activities"))
        self.tab2.layout.addWidget(Calendar(), stretch = 1)
        self.tab2.layout.addWidget(ActivitySimulation())
        self.tab2.layout.addWidget(GenerationWindow("activities"))
        self.tab2.setLayout(self.tab2.layout)

        # Tab : Simulation
        self.tab3.layout = QHBoxLayout(self)
        self.tab3.layout.addWidget(DialogSensorsWindow())
        self.tab3.layout.addWidget(DialogActivitiesWindow())
        self.tab3.layout.addWidget(SimulationWindow())
        self.tab3.setLayout(self.tab3.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


class FileBox(QWidget):
    fileName = 'test' 

    def __init__(self, type, parent = None):
        super(FileBox, self).__init__(parent)


        form_layout = QFormLayout()
        self.file = QLineEdit(self)
        self.file.textChanged.connect(self.setFileName)
        if type == "sensors" :
            form_layout.addRow("Filename (.json):", self.file)
        if type == "activities" :
            form_layout.addRow("Filename (.json):", self.file)
        if type == "output" :
            form_layout.addRow("Filename (.json):", self.file)
        self.setLayout(form_layout)

    def setFileName(self, text):
        FileBox.fileName = text


class AppartmentBox(QWidget):
    appartment = ""
    index = ""
    listObj = {}

    def __init__(self, parent = None):
        super(AppartmentBox, self).__init__(parent)

        self.layout = QHBoxLayout(self)

        self.listAppartment = QListWidget()
        self.listAppartment.insertItem(0, "Appartment 1 - Virtual-Home")
        self.listAppartment.insertItem(1, "Appartment 2 - Virtual-Home")
        self.listAppartment.insertItem(2, "Appartment 3 - Virtual-Home")
        self.listAppartment.insertItem(3, "Appartment 4 - Virtual-Home")
        self.listAppartment.insertItem(4, "Appartment 5 - Virtual-Home")
        self.listAppartment.insertItem(5, "Appartment 6 - Virtual-Home")
        self.listAppartment.insertItem(6, "Appartment 7 - Virtual-Home")
        self.listAppartment.insertItem(7, "Appartment Living Lab IMT Atlantique")
        self.listAppartment.insertItem(8, "Appartment 5 with outside room - Virtual-home")
        self.listAppartment.insertItem(9, "Appartment hh101 - CASAS")

        self.listAppartment.clicked.connect(self.clicked)

        self.textRead = QTextEdit()
        self.textRead.setReadOnly(True)

        self.layout.addWidget(self.listAppartment)
        self.layout.addWidget(self.textRead)
        self.setLayout(self.layout)


    def clicked(self, qmodelindex):
        item = self.listAppartment.currentItem()
        AppartmentBox.appartment = item.text()
        AppartmentBox.index = self.listAppartment.currentRow()
        roomsData = self.readRooms(AppartmentBox.index)
        self.displayRoomsData(roomsData)
        self.readConfig(AppartmentBox.index)

        try : # to remove the instance of last widget SensorsWindow()
            self.layout.itemAt(2).widget().deleteLater()
            self.layout.addWidget(SensorsWindow())
        except AttributeError: 
            self.layout.addWidget(SensorsWindow())
            

    def readConfig(self, indexAppartment):
        fileConfig=open('config/configAppartment' + str(indexAppartment) + '.json', 'r')
        dataFileConfig = json.load(fileConfig)
        #print(dataFileConfig)

        AppartmentBox.listObj['kitchen'] = []
        AppartmentBox.listObj['livingroom'] = []
        AppartmentBox.listObj['bathroom'] = []
        AppartmentBox.listObj['bedroom'] = []
        AppartmentBox.listObj['outside'] = []
        AppartmentBox.listObj['entrance'] = []

        for obj in dataFileConfig['objects'] : 
            id_obj = dataFileConfig['objects'][obj]['id']
            sensor_equiped = dataFileConfig['objects'][obj]['sensorEquiped']
            if id_obj != "" and sensor_equiped != []:
                custom_name = obj
                room = dataFileConfig['objects'][obj]['room']
                AppartmentBox.listObj[room].append(custom_name)

        for presenceSensor in dataFileConfig['presenceSensors'] : 
                name =  dataFileConfig['presenceSensors'][presenceSensor]['floor']
                room = dataFileConfig['presenceSensors'][presenceSensor]['room']
                if name in AppartmentBox.listObj[room] :
                    pass
                else :
                    AppartmentBox.listObj[room].append(name)


    def readRooms(self, index):
        f = open('config/rooms.json')
        data = json.load(f)
          
        roomsData = {}
        index = "% s" % index
        for room in range(len(data[index])):
            name = data[index][room]['class_name']
            center = [round(num,2) for num in data[index][room]['bounding_box']['center']]
            size = [round(num,2) for num in data[index][room]['bounding_box']['size']]
            position = [round(num,2) for num in data[index][room]['obj_transform']['position']]
            roomsData[room] = [name, position, center, size]
        f.close()
        return roomsData

    def displayRoomsData(self, roomsData):
        text = ""
        for index in roomsData : 
            text += str(roomsData[index][0]) + " :\tposition : [" + str(roomsData[index][1]).strip('[]') + "] \n\tcenter : [" + str(roomsData[index][2]).strip('[]') + "]\n\tsize : [" + str(roomsData[index][3]).strip('[]') + "]\n\n"
        self.textRead.setPlainText(text)


class SensorsWindow(QWidget):
    global sensors
            
    def __init__(self, parent = None):
        super(SensorsWindow, self).__init__(parent)

        general_layout = QHBoxLayout(self)
        #layout.setContentsMargins(50,30,50,30)
        general_layout.setSpacing(10)

        # Kitchen 
        kitchen_box = QGroupBox("Kitchen")
        kitchen_layout = QVBoxLayout()
        kitchen_layout.name = "kitchen"

        self.displaySensorRoom(kitchen_layout)

        kitchen_box.setLayout(kitchen_layout)
        general_layout.addWidget(kitchen_box)
        self.setLayout(general_layout)

        # Livingroom
        livingroom_box = QGroupBox("Livingroom")
        livingroom_layout = QVBoxLayout()  
        livingroom_layout.name = "livingroom"

        livingroom_box.setLayout(livingroom_layout)
        general_layout.addWidget(livingroom_box)
        self.setLayout(general_layout)

        self.displaySensorRoom(livingroom_layout)
        
        # Bedroom
        bedroom_box = QGroupBox("Bedroom")
        bedroom_layout = QVBoxLayout() 
        bedroom_layout.name = "bedroom"

        bedroom_box.setLayout(bedroom_layout)
        general_layout.addWidget(bedroom_box)
        self.setLayout(general_layout)

        self.displaySensorRoom(bedroom_layout)

        # Bathroom
        bathroom_box = QGroupBox("Bathroom")
        bathroom_layout = QVBoxLayout() 
        bathroom_layout.name = "bathroom"

        bathroom_box.setLayout(bathroom_layout)
        general_layout.addWidget(bathroom_box)
        self.setLayout(general_layout)

        self.displaySensorRoom(bathroom_layout)

        # Outside
        outside_box = QGroupBox("Outside")
        outside_layout = QVBoxLayout() 
        outside_layout.name = "outside"

        outside_box.setLayout(outside_layout)
        general_layout.addWidget(outside_box)
        self.setLayout(general_layout)

        self.displaySensorRoom(outside_layout)

        # Entrance
        entrance_box = QGroupBox("entrance")
        entrance_layout = QVBoxLayout() 
        entrance_layout.name = "entrance"

        entrance_box.setLayout(entrance_layout)
        general_layout.addWidget(entrance_box)
        self.setLayout(general_layout) 

        self.displaySensorRoom(entrance_layout)
    

    def displaySensorRoom(self, layout):
        room = layout.name
        for element in AppartmentBox.listObj[room] :
            self.createSensor(element, room, layout)

    def onCheckedSensor(self):
        check_button = self.sender()
        #print("Sensor " + (check_button.sensor) + " is " + str(check_button.isChecked()))
        self.setSensor(check_button.sensor)

    def createSensor(self, name, room, layout):
        btn = QCheckBox(name)
        btn.setChecked(False)
        self.initSensor(name, room)
        btn.sensor = name
        btn.toggled.connect(self.onCheckedSensor)
        layout.addWidget(btn)
        return btn

    def initSensor(self, custom_name, room):
        sensors[room][custom_name] = 'no'

    def setSensor(self, custom_name):
        for room in sensors :
            for element in sensors[room] :
                if element == custom_name :
                    if sensors[room][custom_name] == 'no' :
                        sensors[room][custom_name] = 'yes'
                    else :
                        sensors[room][custom_name] = 'no'
                

class GenerationWindow(QWidget):
    global sensors, activities

    def __init__(self, type, parent = None):
        super(GenerationWindow, self).__init__(parent)
        layout = QVBoxLayout(self)
        if type == "sensors" :
            self.btn_generate = QPushButton("Generate json file")
            self.btn_generate.clicked.connect(self.generateSensors)
        if type == "activities" :
            self.btn_generate = QPushButton("Generate json file")
            self.btn_generate.clicked.connect(self.generateActivities)

        layout.addWidget(self.btn_generate)
        self.setLayout(layout)
 
    def generateSensors(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText('Do you want to generate ' + str(FileBox.fileName) + '.json file?')
        msgBox.setWindowTitle("Generate")
        msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgBox.setDefaultButton(QMessageBox.Yes)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            print('input/sensors/' + FileBox.fileName + '.json generated')
            with open('input/sensors/' + FileBox.fileName + '.json', 'w') as f :
                sensorsScene = {}
                sensorsScene["indexAppartment"] = AppartmentBox.index
                sensorsScene["sensors"] = sensors
                json.dump(sensorsScene, f, indent=4, ensure_ascii = False, sort_keys = False)

    def generateActivities(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText('Do you want to generate ' + str(FileBox.fileName) + '.json file?')
        msgBox.setWindowTitle("Generate")
        msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgBox.setDefaultButton(QMessageBox.Yes)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            print('input/activities/' + FileBox.fileName + '.json generated')
            with open('input/activities/' + FileBox.fileName + '.json', 'w') as f :
                json.dump(activities, f, indent=4, ensure_ascii = False, sort_keys = False)

class DialogSensorsWindow(QWidget):

    fileSensors = ""

    def __init__(self, parent = None):
        super(DialogSensorsWindow, self).__init__(parent)

        self.uploadBtn = QPushButton('Upload Sensors Json file')
        self.uploadBtn.clicked.connect(self.getJsonFile)

        self.textRead = QTextEdit()
        self.textRead.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.uploadBtn)
        layout.addWidget(self.textRead)
        self.setLayout(layout)

    def getJsonFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Json File', r"<Default dir>", "Json files (*.json)")
        self.getTextFile(file_name)

    def getTextFile(self, file):
        DialogSensorsWindow.fileSensors = file
        with open(file, 'r') as f :
            data = f.read()
            self.textRead.setPlainText(data)
            f.close()

class DialogActivitiesWindow(QWidget):

    fileActivities = ""

    def __init__(self, parent = None):
        super(DialogActivitiesWindow, self).__init__(parent)

        self.uploadBtn = QPushButton('Upload Activities Json file')
        self.uploadBtn.clicked.connect(self.getActivityFile)

        self.textRead = QTextEdit()
        self.textRead.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.uploadBtn)
        layout.addWidget(self.textRead)
        self.setLayout(layout)

    def getActivityFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Json File', r"<Default dir>", "Json files (*.json)")
        self.getTextFile(file_name)

    def getTextFile(self, file):
        DialogActivitiesWindow.fileActivities = file
        with open(file, 'r') as f :
            data = f.read()
            self.textRead.setPlainText(data)
            f.close()


class Calendar(QWidget):
    global activities
    date = ""
    def __init__(self, parent = None):
        super(Calendar, self).__init__(parent)
        self.initUI()
		
    def initUI(self):
	
        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.move(500, 0)
        cal.clicked[QDate].connect(self.setDate)

        date = cal.selectedDate()
		
    def setDate(self, date):
        Calendar.date = date.toString(QtCore.Qt.ISODate)
        Calendar.date = datetime.datetime.strptime(Calendar.date, "%Y-%m-%d").strftime("%d-%m-%Y")
        activities["config"]["date"] = Calendar.date

class ActivitySimulation(QWidget):
    global activities

    activity = ""
    startTime = ""
    initRoom = "bedroom"
    script = ""
    duration = "00:00"
    accelerationTime = 1
    listActivities = [["StartTime", ""], ["", ""], ["Activity", "Time"]]

    def __init__(self, parent = None):
        super(ActivitySimulation, self).__init__(parent)
        global grid
        grid = QGridLayout(self)

        activity_box = QGroupBox()
        form_layout = QFormLayout()

        self.startTime =  QLineEdit(self)
        self.startTime.textChanged.connect(self.setStartTime)
        form_layout.addRow("StartTime (format 00:00) :", self.startTime)
        
        self.acceleration = QLineEdit(self)
        self.acceleration.textChanged.connect(self.setAcceleration)
        form_layout.addRow("Acceleration (1 to 4) :", self.acceleration)

        self.initRoom = QLineEdit(self)
        self.initRoom.textChanged.connect(self.setInitRoom)
        form_layout.addRow("Init room (outside, bedroom, kitchen, livingroom, bathroom, entrance) :", self.initRoom)

        self.duration = QLineEdit(self)
        self.duration.textChanged.connect(self.setDuration)
        form_layout.addRow("Duration (format 00:00) :", self.duration)



        activity_box.setLayout(form_layout)
        

        self.mainIndex = 1
        self.secondIndex = 1

        path_dir = os.getcwd() + "/input/scripts"

        folders = os.listdir(path_dir)
        if ".DS_Store" in folders : # MacOs users
            folders.remove(".DS_Store")

        for folder in folders :
            self.createActivityButton(folder, grid)

        self.btn_add = QPushButton("Add this activity")
        self.btn_add.clicked.connect(self.addActivity)

        self.tablemodel = TableActivities()
        self.tableview = QTableView()
        self.tableview.resizeColumnsToContents()
        self.tableview.setModel(self.tablemodel)

        grid.addWidget(activity_box, 0, 0)
        grid.addWidget(self.btn_add, self.mainIndex+1, 0)
        grid.addWidget(self.tableview, 0, 2, 15, 15)
        self.setLayout(grid)
        self.setWindowTitle("Activity")

    def createActivityButton(self, name, mainGrid):
        self.btn = QRadioButton(name)
        self.btn.setChecked(False)
        self.btn.name = name
        self.btn.grid = mainGrid
        self.btn.toggled.connect(self.onClickedActivity)
        mainGrid.addWidget(self.btn, self.mainIndex, 0)
        self.mainIndex+=1
    
    def getScriptsName(self, name, mainGrid):
        path_dir = os.getcwd() + "/input/scripts/" + name
        scripts = os.listdir(path_dir)
        if ".DS_Store" in scripts : # MacOs users
            scripts.remove(".DS_Store")
        for script in scripts :
            script = script.replace(".txt", "")
            self.createScriptsButton(script, mainGrid)

    def createScriptsButton(self, nameScript, mainGrid):
        self.secondBtn = QRadioButton(nameScript)
        self.secondBtn.setChecked(False)
        self.secondBtn.name = nameScript
        self.btn.grid = mainGrid
        self.secondBtn.toggled.connect(self.onClickedScript)
        mainGrid.addWidget(self.secondBtn, self.secondIndex, 1)
        self.secondIndex +=1
        
    def onClickedActivity(self):
        global grid
        radioBtn = self.sender()
        print("RadioBtnName : ", radioBtn.name)
    
        try : # to remove last widgetd 
            nbWidgets = grid.count()
            print("nbWidgets : ", nbWidgets)
            for i in range(19,nbWidgets):
                grid.itemAt(i).widget().deleteLater()
                self.secondIndex = 1
            self.getScriptsName(radioBtn.name, radioBtn.grid)

        except AttributeError: 
            self.getScripsName(radioBtn.name, radioBtn.grid)

        ActivitySimulation.activity = radioBtn.name
        print("clicked on ", ActivitySimulation.activity)

    def onClickedScript(self):
        secondRadioBtn = self.sender()
        try : 
            print("secondRadioBtn ", secondRadioBtn)
            ActivitySimulation.script = secondRadioBtn.name
        except AttributeError : 
            pass
    def setStartTime(self, text):
        ActivitySimulation.startTime = text
        activities["config"]["startTime"] = ActivitySimulation.startTime

    def setDuration(self, text):
        ActivitySimulation.duration = text
    
    def setAcceleration(self, text):
        ActivitySimulation.acceleration = text
        activities["config"]["accelerationTime"] = float(ActivitySimulation.accelerationTime)
    
    def setInitRoom(self, text):
        ActivitySimulation.initRoom = text
        activities["config"]["initRoom"] = ActivitySimulation.initRoom

    def addActivity(self):
        #print("Add activity : " + ActivitySimulation.activity + " at time : " + ActivitySimulation.duration)
        #activities["activities"][ActivitySimulation.activity] = ActivitySimulation.duration

        print(self.listActivities)
        nb = 0
        for list in self.listActivities :
            if ActivitySimulation.activity in list[0] :
                nb += 1 
        newIndex = nb + 1
        ActivitySimulation.activity = ActivitySimulation.activity + " " + str(newIndex)

        activities["activities"][ActivitySimulation.activity] = {}
        activities["activities"][ActivitySimulation.activity]["script"] = str(ActivitySimulation.script + ".txt")
        activities["activities"][ActivitySimulation.activity]["duration"] = ActivitySimulation.duration

        self.listActivities[0][1] = ActivitySimulation.startTime

        self.listActivities.append([ActivitySimulation.activity, ActivitySimulation.duration])
        self.tablemodel.refresh()


class TableActivities(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = ActivitySimulation.listActivities

    def rowCount(self, parent):
        return len(self.arraydata)
    
    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.EditRole:
            print( "edit mode" )
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.arraydata[index.row()][index.column()]

    def refresh(self):
        self.arraydata = ActivitySimulation.listActivities
        self.layoutChanged.emit()

class SimulationWindow(QWidget):
    global sensors, activities

    def __init__(self, parent = None):
        super(SimulationWindow, self).__init__(parent)
        layout = QVBoxLayout(self)

        self.btn_simulate = QPushButton("Simulate")
        self.btn_simulate.clicked.connect(self.simulate)

        layout.addWidget(FileBox("output")) # to choose a name for the .csv database file
        layout.addWidget(self.btn_simulate)
        self.setLayout(layout)

    def simulate(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Do you want to simulate this files uploaded and created the database file: " + FileBox.fileName + ".json " +  FileBox.fileName + ".csv ?")
        msgBox.setWindowTitle("Simulate")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            outputFile = FileBox.fileName
            l = simulation5.Link(DialogSensorsWindow.fileSensors, DialogActivitiesWindow.fileActivities, outputFile)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

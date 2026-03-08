# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QWidget ,QListView
from PySide6.QtCore import * #QFile, QIODevice, Slot ,QStringListModel,QItemSelection
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget
from sqlite3 import *
from BLE import BLE
from mcsv import *
import asyncio
from model import model

MODEL_NBR_UUID = "df1413de-2317-4dca-8b04-551ccc2f399b"
left_address  = "3C:DC:75:31:80:92"
right_address = "3C:DC:75:31:80:00"


hand_name = "J_Bip_L_Hand"

bond_name = [["J_Bip_L_Thumb1","J_Bip_L_Thumb2","J_Bip_L_Thumb3"],
            ["J_Bip_L_Index1","J_Bip_L_Index2","J_Bip_L_Index3"],
            ["J_Bip_L_Middle1","J_Bip_L_Middle2","J_Bip_L_Middle3"],
            ["J_Bip_L_Ring1","J_Bip_L_Ring2","J_Bip_L_Ring3"],
            ["J_Bip_L_Little1","J_Bip_L_Little2","J_Bip_L_Little3"]]

class PAK_E(Enum):
    PAK_TIME = 0,
    PAK_POS_X = 1,
    PAK_POS_Y = 2,
    PAK_POS_Z = 3,
    PAK_FINGER_1 = 4,
    PAK_FINGER_2 = 5,
    PAK_FINGER_3 = 6,
    PAK_FINGER_4 = 7,
    PAK_FINGER_5 = 8,

class Widget(QWidget):

    my_csv = mcsv("data.csv")

    #当前的
    gestureID = 0
    recordIndex = 0
    logAble = 0

    recordStatus = 0
    leftStartTime = 0
    leftPak = []
    rightStartTime = 0
    rightPak = []

    def __init__(self, parent=None):
        #初始化
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        #信号连接
        self.ui.lineEditName.editingFinished.connect(self.gestureRename)

        self.ui.pushButtonRecordStart.clicked.connect(self.startRecord)
        self.ui.pushButtonRecordEnd.clicked.connect(self.endRecord)
        self.ui.pushButtonRecordReview.clicked.connect(self.replayRecord)
        self.ui.pushButtonRecordNew.clicked.connect(self.recordNew)
        self.ui.pushButtonClearLog.clicked.connect(self.clearLog)

        self.ui.pushButtonGestureNew.clicked.connect(self.gestureNew)
        self.ui.pushButtonGestureDel.clicked.connect(self.gestureDel)
        self.ui.pushButtonRecordDel.clicked.connect(self.recordDel)
        #手势筛选
        self.ui.lineEditSearch.textChanged.connect(self.searchGesture)
        self.model = QStringListModel()
        self.ui.gestureListView.setModel(self.model)
        self.ui.gestureListView.selectionModel().currentChanged.connect(self.gestureSelect)

        self.ui.comboBoxRecord.activated.connect(self.recordSelect)

        self.update()
        self.logAble = 1

        self.myble = BLE();
        self.myble.init(left_address,right_address,MODEL_NBR_UUID)
        self.myble.leftReceive.connect(self.bleLeftReceive)
        self.myble.leftStatus.connect(self.bleLeftStatus)
        self.bleLeftStatus(0)
        self.myble.rightReceive.connect(self.bleRightReceive)
        self.myble.rightStatus.connect(self.bleRightStatus)
        self.bleRightStatus(0)
        self.myble.start()

        global hand_name
        global bond_name
        self.my_model(hand_name,bone_name)

    def log(self,text):
        if self.logAble:
            self.ui.logBrowser.append(text)

    def plainLog(self,text):
        if self.logAble:
            self.ui.logBrowser.insertPlainText(text)

    @Slot()
    def clearLog(self):
        self.ui.logBrowser.setText('')

    @Slot()
    def searchGesture(self):
        list = []
        list = self.my_csv.gestureFilter(self.ui.lineEditSearch.text())
        if list == []:
            #self.log("找不到对应ID/名字的手势")
            self.model.setStringList([])
        else:
            strList = []
            for row in list:
                str = f"{row['id']}.{row['name']}"
                if row['name'] == '':
                    str+="(未命名)"
                if str not in strList:
                    strList.append(str)
            self.model.setStringList(strList)

    @Slot()
    def startRecord(self):
        if self.unselectError() == 1:
            return
        #self.my_csv.printGesture()
        self.recordStatus = 1
        self.log("开始录制")

    @Slot()
    def endRecord(self):
        if self.unselectError() == 1:
            return
        self.recordStatus = 0
        self.leftStartTime = 0
        self.rightStartTime = 0
        mixPak = []
        llen = len(self.leftPak)
        rlen = len(self.rightPak)
        if llen >= rlen:
            for i,s in enumerate(self.leftPak):
                if i < rlen:
                    str = f"{self.leftPak[i]}:{self.rightPak[i]}"
                else:
                    str = f"{self.leftPak[i]}:"
                mixPak.append(str)
        elif llen < rlen:
            for i,s in enumerate(self.rightPak):
                if i < llen:
                    str = f"{self.leftPak[i]}:{self.rightPak[i]}"
                else:
                    str = f":{self.rightPak[i]}"
                mixPak.append(str)
        self.my_csv.writeRecord(self.gestureID,self.recordIndex,mixPak)
        self.log("结束录制")

    @Slot()
    def replayRecord(self):
        if self.unselectError() == 1:
            return
        self.log("回放中")

    @Slot()
    def recordNew(self):
        if self.unselectError() == 1:
            return
        recordIndex = self.my_csv.addRecord(self.gestureID)-1
        self.log(f"新录制:{recordIndex}")
        self.recordIndex = recordIndex
        self.update()

    @Slot()
    def gestureRename(self):
        if self.unselectError() == 1:
            return
        if self.ui.lineEditName.text()=='':
            self.log("名字不能为空!")
        else:
            name = self.ui.lineEditName.text()
            self.my_csv.gestureRename(self.gestureID,name)
            self.log(f"ID为[{self.gestureID}]的手势重命名为:{name}")
            self.update()

    @Slot()
    def gestureNew(self):
        self.gestureID = self.my_csv.gestureNew();
        self.log(f"创建新手势ID:{self.gestureID}")
        self.update()

    @Slot()
    def gestureSelect(self,current: QModelIndex):
        if current.isValid():
            text = current.data()
            #1.(name)
            ss = text.split('.')
            i = int(ss[0])
            self.gestureID = i
            self.log(f"选中:{i} {ss[1]}")
            self.update()

    @Slot()
    def recordSelect(self,index: QModelIndex):
        self.recordIndex=index
        self.log(f"切换为录制：{self.recordIndex}")

    @Slot()
    def recordDel(self):
        if self.recordIndex < 0:
            self.log("未选择录制")
            return
        lenth = self.my_csv.delRecord(self.gestureID,self.recordIndex)
        if lenth == 1:
            self.log(f"删除了录制{self.recordIndex},并新建了一个空录制")
        else:
            self.log(f"删除了录制{self.recordIndex},索引已更新")
        self.recordIndex = -1   #防止连击误删除
        self.update()

    @Slot()
    def gestureDel(self):
        self.my_csv.gestureDel(self.gestureID)
        self.log(f"删除手势:{self.gestureID}")
        self.gestureID = 0
        self.update()

    def unselectError(self):
        if self.gestureID == 0:
            self.log("未选中手势!")
            return 1
        return 0

    def update(self):
        #更新id
        if self.gestureID == 0:
            self.ui.labelId.setText("未选择")
        else:
            self.ui.labelId.setText(f"{self.gestureID}")
        #更新名字
        if self.gestureID != 0:
            gesture = self.my_csv.getRecords(self.gestureID)
            self.ui.lineEditName.setText(gesture[0]['name'])
        #更新手势搜索
        self.searchGesture()
        #更新录制数
        self.ui.comboBoxRecord.clear()
        list = self.my_csv.getRecords(self.gestureID)
        for i,row in enumerate(list):
            self.ui.comboBoxRecord.addItem(str(i))
        self.ui.comboBoxRecord.setCurrentIndex(self.recordIndex)

    @Slot()
    def bleLeftReceive(self,str):
        if str == '':
            return
        pak = [float(num) for num in str.split(',')]
        if self.recordStatus == 0:
            self.leftStartTime = 0
        elif self.recordStatus == 1 and self.leftStartTime == 0:
            self.leftStartTime = pak[0]
            self.leftPak.clear()
        else:
            print(pak[0]-self.leftStartTime,self.leftStartTime,len(self.leftPak))
            self.leftPak.append(str)
            self.plainLog(".")
    @Slot()
    def bleLeftStatus(self,status):
        if status == 1:
            self.ui.labelLeftStatus.setText("已连接")
            self.ui.labelLeftStatus.setStyleSheet("color: green;")
        else:
            self.ui.labelLeftStatus.setText("连接断开")
            self.ui.labelLeftStatus.setStyleSheet("color: red;")

    def bleRightReceive(self,pak):
        pak = [float(num) for num in str.split(',')]
        if self.recordStatus == 0:
            self.rightStartTime = 0
        elif self.recordStatus == 1 and self.rightStartTime == 0:
            self.rightStartTime = pak[0]
            self.rightPak.clear()
        else:
            print(pak[0]-self.rightStartTime,self.rightStartTime,len(self.rightPak))
            self.rightPak.append(str)
            self.plainLog(".")
    @Slot()
    def bleRightStatus(self,status):
        if status == 1:
            self.ui.labelRightStatus.setText("已连接")
            self.ui.labelRightStatus.setStyleSheet("color: green;")
        else:
            self.ui.labelRightStatus.setText("连接断开")
            self.ui.labelRightStatus.setStyleSheet("color: red;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())


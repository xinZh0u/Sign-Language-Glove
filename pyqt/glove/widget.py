# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QWidget ,QListView
from PySide6.QtCore import QFile, QIODevice, Slot ,QStringListModel,QItemSelection
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_Widget
from sqlite3 import *
from BLE import BLE
from mcsv import *
import asyncio

MODEL_NBR_UUID = "df1413de-2317-4dca-8b04-551ccc2f399b"
left_address  = "3C:DC:75:31:80:92"
right_address = "3C:DC:75:31:80:00"

class GestureData:
    id = 0      #
    name = ""   #翻译后的名字
    paks = []   #数据包
    def __init__(self):
        pass

my_csv = mcsv("data.csv")

class Widget(QWidget):
    global my_ble
    global my_csv

    #当前的
    gestureID = 0
    recordIndex = 0
    logAble = 0

    gestureData = GestureData()
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

        self.ui.pushButtonRecordDel.clicked.connect(self.recordDel)
        #手势筛选
        self.ui.lineEditSearch.textChanged.connect(self.searchGesture)
        self.model = QStringListModel()
        self.ui.gestureListView.setModel(self.model)
        self.ui.gestureListView.selectionModel().currentChanged.connect(self.gestureSelect)

        self.ui.comboBoxRecord.activated.connect(self.recordSelect)

        self.update()
        self.logAble = 1

    def log(self,text):
        if self.logAble:
            self.ui.logBrowser.append(text)

    @Slot()
    def clearLog(self):
        self.ui.logBrowser.setText('')

    @Slot()
    def searchGesture(self):
        list = []
        list = my_csv.gestureFilter(self.ui.lineEditSearch.text())
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
        my_csv.printGesture()
        self.log("开始录制")

    @Slot()
    def endRecord(self):
        if self.unselectError() == 1:
            return
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
        recordIndex = my_csv.addRecord(self.gestureID)-1
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
            my_csv.gestureRename(self.gestureID,name)
            self.log(f"ID为[{self.gestureID}]的手势重命名为:{name}")
            self.update()

    @Slot()
    def gestureNew(self):
        self.gestureID = my_csv.gestureNew();
        self.log(f"创建新手势ID:{self.gestureID}")
        self.update()

    @Slot()
    def gestureSelect(self,current: QModelIndex):
        if current.isValid():
            text = current.data()
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
        lenth = my_csv.delRecord(self.gestureID,self.recordIndex)
        if lenth == 1:
            self.log(f"删除了录制{self.recordIndex},并新建了一个空录制")
        else:
            self.log(f"删除了录制{self.recordIndex},索引已更新")
        self.recordIndex = -1   #防止连击误删除
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
            gesture = my_csv.getRecords(self.gestureID)
            self.ui.lineEditName.setText(gesture[0]['name'])
        #更新手势搜索
        self.searchGesture()
        #更新录制数
        self.ui.comboBoxRecord.clear()
        list = my_csv.getRecords(self.gestureID)
        for i,row in enumerate(list):
            self.ui.comboBoxRecord.addItem(str(i))
        self.ui.comboBoxRecord.setCurrentIndex(self.recordIndex)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())

my_ble = BLE(left_address,right_address,MODEL_NBR_UUID)

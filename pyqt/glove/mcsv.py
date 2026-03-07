#手势csv数据文件存储模式

#  id    name   data(PS:详细对应关系在PAK_E)
# (id1) ("A")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id1) ("A")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id1) ("A")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id2) ("B")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id2) ("B")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id3) ("C")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
# (id4) ("D")  ("1.0,2.1,3.2,...") ("1.0,2.1,3.2,...") ...
#  ...

import csv
import pandas as pd
from enum import Enum

class PAK_E(Enum):
    TIME = 0,
    PAK_POS_X = 1,
    PAK_POS_Y = 2,
    PAK_POS_Z = 3,
    PAK_FINGER_1 = 4,
    PAK_FINGER_2 = 5,
    PAK_FINGER_3 = 6,
    PAK_FINGER_4 = 7,
    PAK_FINGER_5 = 8,

class mcsv:
    fileName = ""
    fieldnames = None
    def __init__(self,name):
        self.fileName = name
        self.fieldnames = ['id', 'name']
        with open(self.fileName, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    def printGesture(self):
        print(f"name:{self.fileName}")
        with open(self.fileName, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i,row in enumerate(reader):
                print(f"i:{i}",row['id'],row['name'])

    def gestureRename(self,gestureId,gestureName):
        if gestureId == 0:
            return
        with open(self.fileName, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            df = pd.read_csv(self.fileName)
            for i,row in enumerate(reader):
                id = int(row['id'])
                #print(f"i:{i}")
                if id == gestureId:
                    # 修改名字
                    df.iloc[i, 1] = gestureName
            # 保存回文件（保留索引和标题）
            df.to_csv(self.fileName, index=False)

    def getRecords(self,id):
        if id == 0:
            return []
        list = []
        with open(self.fileName, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i,row in enumerate(reader):
                row_id = int(row['id'])
                if row_id == id:
                    list.append(row)
        return list

    def addRecord(self,id):
        if id == 0:
            return
        new_name = ''
        list = self.getRecords(id)
        if list != []:
            new_name = list[0]['name']
        new_row = {'id': id,'name':new_name}
        df = pd.read_csv(self.fileName)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.fileName, index=False)
        records =  self.getRecords(id)
        i = 0
        for record in records:
            i+=1
        return i

    def delRecord(self,gesture_id,index):
        df = pd.read_csv(self.fileName)
        filtered_df = df[df['id'] == gesture_id]
        lenth = len(filtered_df)

        if index < lenth:
            indices = df[df['id'] == gesture_id].index
            df = df.drop(indices[index])
            df.to_csv(self.fileName, index=False)
            if lenth == 1:
                self.addRecord(gesture_id)
        return lenth

    def openCsv():
        with open(self.fileName, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            data_list = list(reader)

    #手势过滤(过滤id或者名字)
    def gestureFilter(self,str):
        list = []
        with open(self.fileName, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for i,row in enumerate(reader):
                if str=='':
                    list.append(row)
                    continue
                #过滤id
                id = int(row['id'])
                str_id = 0
                try:
                    str_id = int(str)
                    if str_id == id:

                        list.append(row)
                except:
                    str_id = 0
                #过滤名字
                name = row['name']
                if str in name:
                    list.append(row)
        return list

    def gestureNew(self):
        new_id = 0
        with open(self.fileName, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            id_max = 0
            for i,row in enumerate(reader):
                id = int(row['id'])
                if id_max == 0:
                    id_max = id
                elif id_max < id:
                    id_max = id
            new_id = id_max+1
        if new_id !=0:
            self.addRecord(new_id)
        return new_id

import sys
import math
from enum import Enum , auto
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *

# 设备ID枚举
class Dev(Enum):
  CENTER  = 0
  L_BIG   = auto()
  L_SMALL = auto()
  L_GLOVE = auto()
  R_BIG   = auto()
  R_SMALL = auto()
  R_GLOVE = auto()
  NUM = auto()
  
  OFFLINE = False
  ONLINE  = True
DEV = Dev    

device_icon_path = "icon/device.png"

class BoneChart(QWidget):
    SHOULDER = 12
    BIG = 10
    SMALL = 10
    MAP_WIDTH = 40
    MAP_HEIGHT = 30
    
    bones = [[0,0]] * DEV.NUM.value
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 创建折线序列
        self.line_series = QLineSeries()
        self.line_series.setBrush(QColor(0, 0, 255))
        
        # 创建散点序列
        self.scatter_series = QScatterSeries()
        self.scatter_series.setMarkerSize(10.0)  
        self.scatter_series.setBrush(QColor(255, 0, 0))
            
        # 创建图表对象
        self.chart = QChart()
        self.chart.legend().hide()


        # 创建图表视图
        chart_view = QChartView(self.chart)
    
        self.update_chart([[0,0,0],[0,0,0]])
        self.chart.addSeries(self.line_series)
        self.chart.addSeries(self.scatter_series)
        layout.addWidget(chart_view)
        
        # 隐藏网格线
        self.axis_x = QValueAxis()
        self.axis_x.setMax(self.MAP_WIDTH)
        self.axis_x.setTitleText("X 轴")
        self.axis_x.setVisible(False)
        self.axis_x.setLabelFormat("%.1f")
        self.axis_x.setGridLineVisible(False)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.line_series.attachAxis(self.axis_x)
        self.scatter_series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setMax(self.MAP_HEIGHT)
        self.axis_y.setVisible(False)
        self.axis_y.setTitleText("Y 轴")
        self.axis_y.setLabelFormat("%.2f")
        self.line_series.attachAxis(self.axis_y)
        self.scatter_series.attachAxis(self.axis_y)
        
        self.axis_y.setGridLineVisible(False)  
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.line_series.attachAxis(self.axis_y)
        self.scatter_series.attachAxis(self.axis_y)
        
        self.update_chart([[10,10,10],[0,0,0]])
    
    def update_chart(self,bones):
        # 添加数据点 (模拟 sin(x))
        self.line_series.clear()
        self.scatter_series.clear()
        #self.chart.removeAllSeries()
    
        points = [[0,0,0]] * (Dev.NUM.value - 3)
        
        rotate = [[0,0,0]] * Dev.NUM.value
        # x,y，下一个关节的旋转
        
        # 左手
        # yaw = 90
        # pitch = 45
        # roll = 90
        rotate[1] = bones[0]#[pitch,yaw,roll]
        #print(rotate[1])
        points[1] = [self.MAP_WIDTH/2-self.SHOULDER/2, self.MAP_HEIGHT/2,0]
        # x = self.BIG * -math.cos(math.radians(rotate[1][0])) 
        # y = self.BIG * math.sin(math.radians(rotate[1][0])) * math.cos(math.radians(rotate[1][1]))    
        # z = self.BIG * -math.sin(math.radians(rotate[1][1]))
        
        x = self.BIG * -math.cos(math.radians(rotate[1][0])) * math.cos(math.radians(rotate[1][1]))
        y = self.BIG * math.sin(math.radians(rotate[1][0])) #//* math.cos(math.radians(rotate[1][1]))    
        z = self.BIG * -math.sin(math.radians(rotate[1][1]))
        points[0] = [points[1][0]+x, points[1][1]+y, points[1][2] + z] 
        
        # 右手
        # yaw = 0
        # pitch = 0
        # roll = 90
        rotate[2] = bones[1]#[pitch,yaw,roll]
        #print(rotate[1])
        points[2] = [self.MAP_WIDTH/2+self.SHOULDER/2, self.MAP_HEIGHT/2,0]
        x = self.BIG * math.cos(math.radians(rotate[2][0])) * math.cos(math.radians(rotate[2][1]))
        y = self.BIG * math.sin(math.radians(rotate[2][0]))
        z = self.BIG * -math.sin(math.radians(rotate[2][1]))
        points[3] = [points[2][0]+x,points[2][1]+y,points[2][2]+z]
        
        for i,p in enumerate(points):
            self.line_series.append(p[0], p[1])
            self.scatter_series.append(p[0], p[1])
        
        #self.chart.addSeries(self.line_series)
        #self.chart.addSeries(self.scatter_series)
        
        # self.line_series.attachAxis(self.axis_x)
        # self.scatter_series.attachAxis(self.axis_x)
        # self.line_series.attachAxis(self.axis_y)
        # self.scatter_series.attachAxis(self.axis_y)
        self.chart.update()

class DeviceItemWidget(QWidget):
    def __init__(self, icon_path, device_name, device_id,status, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        # 主布局：水平排列
        main_layout = QHBoxLayout(self)
        #main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(15)
        
        # 左侧图标
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(32, 32)
        
        # 右侧垂直布局：设备名 + 状态
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.device_label = QLabel(device_name)
        self.device_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.device_label.setStyleSheet("color: #333;")
        
        
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.set_status(status)
        
        text_layout.addWidget(self.device_label)
        text_layout.addWidget(self.status_label)
        text_layout.setAlignment(Qt.AlignTop)
        
        # 组合布局
        main_layout.addWidget(self.icon_label)
        main_layout.addLayout(text_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setFixedHeight(50)
        
    def set_status(self,status):
        if status == DEV.ONLINE.value:
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            self.status_label.setText("在线")
        else:
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.status_label.setText("断开")

class DeviceManager(QWidget):
    devices = []
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设备管理面板")
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout(self)
        
        self.dev_layout = QHBoxLayout(self)
        layout.addLayout(self.dev_layout)
        self.v_layout = QVBoxLayout(self)
        layout.addLayout(self.v_layout)
        
        # 添加示例设备
        self.add_device(device_icon_path, "左手套", DEV.L_GLOVE.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "左小臂", DEV.L_SMALL.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "左大臂", DEV.L_BIG.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "中心"  , DEV.CENTER.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右大臂", DEV.R_BIG.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右小臂", DEV.R_SMALL.value, DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右手套", DEV.R_GLOVE.value, DEV.OFFLINE.value)
        
        # 显示校准的label
        self.cali_label = QLabel()
        self.cali_label.setVisible(False)
        self.cali_label.setFont(QFont("Segoe UI", 14))
        self.cali_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.v_layout.addWidget(self.cali_label)
        
        self.bone_chart = BoneChart()
        self.po = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.bone_chart.setSizePolicy(self.po)
        self.v_layout.addWidget(self.bone_chart)
        
    def add_device(self, icon_path, device_name, device_id,status):
        # 添加一个设备项
        widget = DeviceItemWidget(icon_path, device_name,device_id, status)
        self.dev_layout.addWidget(widget)
        self.devices.append(widget)
    
    def set_device(self,id,status):
        for dev in self.devices:
            if dev.device_id == id:
                dev.set_status(status)
        
    def process_device_message(self,message):
        mes = message.split(':')
        #print(mes)
        if len(mes) < 2:
            return
        self.set_device(int(mes[0]),int(mes[1]))
    
    def process_cali_message(self,message):
        mes = message.split(':')
        #print(mes)
        if len(mes) < 2:
            return
        if mes[0] == '0':
            self.cali_label.setVisible(True)
            self.cali_label.setText(f"校准倒计时:{mes[1]}s")
        if mes[0] == '1':
            self.cali_label.setVisible(False)
            self.cali_label.setText("校准完成！")
    
    def process_rotate_message(self,message):
        mes = [float(num) for num in message.split(',')]
        #print(mes)
        if len(mes) < 6:
            return
        #print("update")
        self.bone_chart.update_chart([mes[0:2],mes[3:5]])
    
    def rotate(self,nums):
        self.bone_chart.update_chart([nums[0:2],nums[3:5]])
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceManager()
    window.show()
    sys.exit(app.exec())

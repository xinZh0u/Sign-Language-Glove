import sys
from enum import Enum , auto
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

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

device_icon_path = "icon/37-01.png"

class DeviceItemWidget(QWidget):
    def __init__(self, icon_path, device_name, status, parent=None):
        super().__init__(parent)
        
        # 主布局：水平排列
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
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
        
        # 列表控件
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.list_widget.setFrameShape(QFrame.NoFrame)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                border-bottom: 1px solid #e9ecef;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-radius: 4px;
            }
        """)
        
        # 添加示例设备
        self.add_device(device_icon_path, "中心", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "左大臂", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "左小臂", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "左手套", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右大臂", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右小臂", DEV.OFFLINE.value)
        self.add_device(device_icon_path, "右手套", DEV.OFFLINE.value)
        
        layout.addWidget(self.list_widget)
        
    def add_device(self, icon_path, device_name, status):
        """添加一个设备项到列表"""
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 50))  # 固定高度
        widget = DeviceItemWidget(icon_path, device_name, status)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        self.devices.append(widget)
    
    def set_device(self,id,status):
        self.devices[id].set_status(status)
        
    def process_device_message(self,message):
        mes = message.split(':')
        print(mes)
        if len(mes) < 2:
            return
        self.set_device(int(mes[0]),int(mes[1]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceManager()
    window.show()
    sys.exit(app.exec())

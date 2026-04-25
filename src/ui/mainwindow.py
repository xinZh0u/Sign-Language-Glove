import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from chatwidget import *
from person_setting import *
from devicewidget import *
from recordwidget import *
from wifi import *

chat_ip = "127.0.0.1"
chat_port = 7399 

class MainWindow(QMainWindow):
    my_wifi = wifi(chat_ip,chat_port)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("知声客户端")
        #self.showFullScreen()
        self.setGeometry(100, 100, 800, 600)
        
        self.my_wifi.get_message.connect(self.recv_message)
        self.my_wifi.start()
        # 创建主容器
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # 左侧导航栏（QListWidget）
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(100)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        self.nav_list.setFont(QFont("Segoe UI", 11))

        # 右侧内容区域（QStackedWidget）
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f8f9fa; border: none;")

        # 添加页面
        self.chat_widget = ChatWidget()
        self.device_widget = DeviceManager()
        self.member_widget = MemberManager()
        self.record_widget = RecordWidget()
        self.add_page("聊天", self.chat_widget)
        self.add_page("设备状态", self.device_widget)
        self.add_page("成员设置", self.member_widget)
        self.add_page("录制", self.record_widget)
        
        self.content_stack.setCurrentIndex(3)
        # 绑定导航事件
        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        # 在这里添加代码设置默认为”录制“页面
        
        # 将左右组件加入主布局
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.content_stack)
                
        # 创建全局退出快捷键
        save_shortcut = QShortcut(QKeySequence("Q"), self)
        save_shortcut.activated.connect(lambda : self.close())

    # 添加页面
    def add_page(self, title, widget):
        self.content_stack.addWidget(widget)
        self.nav_list.addItem(title)

    @Slot()
    def recv_message(self,message):
        if message[0] == '@':
            self.chat_widget.process_chat_message(message[1:])
        if message[0] == '!':
            self.device_widget.process_device_message(message[1:])
        if message[0] == '%':
            self.device_widget.process_cali_message(message[1:])
        if message[0] == 'R':
            self.device_widget.process_rotate_message(message[1:])
            self.record_widget.process_message(message[1:])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

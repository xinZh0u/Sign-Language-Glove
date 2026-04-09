import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                               QHBoxLayout, QLabel, QTextBrowser, QStyle)
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, QSize
from wifi import *

class CustomListItemWidget(QWidget):
    def __init__(self, align, icon_path, label_text, browser_text, parent=None):
        super().__init__(parent)
        
        # 主布局：垂直
        layout = QVBoxLayout(self)
        #layout.setContentsMargins(10, 10, 10, 10)
        #layout.setSpacing(15)

        title_layout = QHBoxLayout()
        if align:
            title_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        #title_layout.setSpacing(5)
        
        # 图标（使用系统图标或自定义路径）
        self.icon_label = QLabel()
        if icon_path:
            icon_pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(icon_pixmap)
        else:
            # 使用系统图标作为默认
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            self.icon_label.setPixmap(icon.pixmap(32, 32))
        self.icon_label.setFixedSize(32, 32)
        title_layout.addWidget(self.icon_label)
        
        
        
        # 标签（加粗，用于标题）
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.label.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(self.label)
        
        # 文本浏览器（支持富文本、自动换行、无边框）
        self.text_browser = QTextBrowser()
        self.text_browser.setHtml(browser_text)
        self.text_browser.setReadOnly(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 6px;
                font-size: 11pt;
                color: #34495e;
            }
        """)
        self.text_browser.setMaximumHeight(120)
        self.text_browser.setMinimumHeight(80)

        layout.addLayout(title_layout)
        layout.addWidget(self.text_browser)
        
        layout.addStretch()  # 右侧留白，使内容左对齐
        
        self.setLayout(layout)

class CustomListWidget(QWidget):
    my_wifi = wifi("127.0.0.1",7399)

    persons_name_map = [
        {
        'id':'myself',
        'name':'我'
        },
        {
        'id':'mjq',
        'name':'马假期'
        },
        {
        'id':'dcx',
        'name':'鼎城系'
        },             
        {
        'id':'syx',
        'name':'宋雅轩'
        }                    
    ]

    items_data = []
    def __init__(self):
        super().__init__()
        self.setWindowTitle("语音识别系统")
        self.resize(600, 500)
        self.my_wifi.get_message.connect(self.recv_message)
        self.my_wifi.start()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0);

        # 创建列表控件
        self.list_widget = QListWidget()
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        #添加多个自定义项
        self.update_list()

    def update_list(self):
        self.list_widget.clear()
        for item_data in self.items_data:
            item_widget = CustomListItemWidget(
                align=item_data['align'],
                icon_path=item_data["icon"],
                label_text=item_data["label"],
                browser_text=item_data["text"]
            )
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
        scrollbar = self.list_widget.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        

    @Slot()
    def recv_message(self,message):
        mes = message.split(':')
        print(mes)
        align = 0 
        id = ""
        if self.items_data!=[] and mes[0]==self.items_data[-1]["id"]:
            self.items_data[-1]["text"]+=mes[1]
        else:
            if mes[0] == 'myself':
                align = 1
            label = mes[0]
            for person in self.persons_name_map:
                if person['id'] == mes[0]:
                    label = person["name"]
            icon = None
            text = mes[1]
            item = {
                'align': align,
                "icon": icon,
                "id": id,
                "label": label,
                "text": text
            }
            self.items_data.append(item)
        self.update_list()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomListWidget()
    window.show()
    sys.exit(app.exec())

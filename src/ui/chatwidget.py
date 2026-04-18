import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from wifi import *
import json

class ChatListItemWidget(QWidget):
    icon_size = 64
    def __init__(self, align, icon_path, label_text, browser_text, parent=None):
        super().__init__(parent)
        
        # 主布局：垂直
        self.layout = QVBoxLayout(self)
        self.title_layout = QHBoxLayout()
    
        # 图标（使用系统图标或自定义路径）
        self.icon_label = QLabel()
        if icon_path:
            icon_pixmap = QPixmap(icon_path).scaled(self.icon_size, self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(icon_pixmap)
        else:
            # 使用系统图标作为默认
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            self.icon_label.setPixmap(icon.pixmap(self.icon_size, self.icon_size))
        self.icon_label.setFixedSize(self.icon_size,self.icon_size)
        
        
        # 标签（加粗，用于标题）
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.label.setStyleSheet("color: #2c3e50;")
        

        if align:
            self.title_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.title_layout.addWidget(self.label)
            self.title_layout.addWidget(self.icon_label)
        else:
            self.title_layout.addWidget(self.icon_label)
            self.title_layout.addWidget(self.label)
        
        self.po = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(self.po)
        
        # 文本浏览器（支持富文本、自动换行、无边框）
        self.text_browser = QTextBrowser()
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        self.text_browser.setSizePolicy(sizePolicy)
        self.text_browser.setHtml(browser_text)
        self.text_browser.setReadOnly(True)
        self.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 20px;
                font-size: 18pt;
                color: #34495e;
            }
        """)
        self.text_browser.setMinimumHeight(80)

        self.layout.addLayout(self.title_layout)
        self.layout.addWidget(self.text_browser)
        
        self.layout.addStretch()  # 右侧留白，使内容左对齐
        
        self.setLayout(self.layout)
    def updateSizeHint(self):
        # 强制重绘并重新计算内容高度
        self.text_browser.document().adjustSize()
        # 获取文档实际高度，加上内边距
        height = self.text_browser.document().size().height() + self.layout.sizeHint().height() #是上下内边距总和
        self.setMinimumHeight(int(height))
        self.setMaximumHeight(int(height))
    
    def sizeHint(self):
        # 重写 sizeHint，让 QListWidget 使用我们计算的高度
        self.updateSizeHint()
        return QSize(self.width(), self.text_browser.document().size().height() + self.layout.sizeHint().height())

class ChatWidget(QWidget):
    # 人物姓名id映射关系
    persons_name_map = []

    items_data = []
    def __init__(self):
        super().__init__()
        self.setWindowTitle("语音识别系统")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0);
        self.setGeometry(100, 100, 1000, 600)

        # 导入人物映射信息
        self.load_persons_map()

        # 创建列表控件
        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
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
        
    # 保存人物映射表    
    def save_persons_map(self):
        print("save json")
        with open('persons_name_map.json', 'w', encoding='utf-8') as f:
            json.dump(self.persons_name_map, f, ensure_ascii=False, indent=4)

    # 加载人物映射表
    def load_persons_map(self):
        print("load json")
        with open('persons_name_map.json', 'r', encoding='utf-8') as f:
            self.persons_name_map = json.load(f)

    # 更新对话列表
    def update_list(self):
        self.list_widget.clear()
        for item_data in self.items_data:
            item_widget = ChatListItemWidget(
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
        
    # 处理对话消息
    def process_chat_message(self,message):
        mes = message.split(':')
        print(mes)
        if len(mes) < 2:
            return
        
        # 后面的被分割的文字合并
        for m in range(len(mes)-2):
            mes[1] += ':' + mes[2+m]
        align = 0 
        
        id = ""
        # 判断id是否有具体的人物对应关系
        if self.items_data!=[] and mes[0]==self.items_data[-1]["id"]:
            # 说话人未改变,对白内容增加
            self.items_data[-1]["text"]+=mes[1]
        else:
            # 说话人改变,创建新消息
            id = mes[0]
            label = mes[0]
            text = mes[1]
            icon = None
            if mes[0] == 'myself':
                align = 1
            
            for person in self.persons_name_map:
                if person['id'] == mes[0]:
                    label = person["name"]
                    icon = person["icon"]
            
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
    window = ChatWidget()
    window.show()
    sys.exit(app.exec())

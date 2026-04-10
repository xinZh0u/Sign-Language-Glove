import sys
import json
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *


class MemberManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("角色成员管理器")
        self.setGeometry(100, 100, 800, 600)

        # 数据存储路径
        self.data_file = "persons_name_map.json"
        self.members = self.load_members()

        # 主控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 输入区域
        input_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("姓名")
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("头像路径")
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_icon)
        self.edit_button = QPushButton("修改")
        self.edit_button.clicked.connect(self.edit_member)
        self.edit_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        self.del_button = QPushButton("删除成员")
        self.del_button.clicked.connect(self.del_member)
        self.del_button.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")

        input_layout.addWidget(QLabel("ID:"))
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(QLabel("姓名:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("头像:"))
        input_layout.addWidget(self.icon_input)
        input_layout.addWidget(self.browse_button)
        input_layout.addWidget(self.edit_button)
        input_layout.addWidget(self.del_button)
        layout.addLayout(input_layout)

        # 成员列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "头像路径"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.refresh_table()

    def load_members(self):
        # 从JSON文件加载成员数据
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "加载失败", f"无法读取数据文件：{str(e)}")
        return []

    def save_members(self):
        # 保存成员数据到JSON文件
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.members, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法写入数据文件：{str(e)}")

    def edit_member(self):
        # 添加新成员，检查ID重复
        _id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        icon = self.icon_input.text().strip()

        # 修改成员
        for member in self.members:
            if member['id'] == _id:
                if name!="":
                    member['name'] = name
                if icon!="":
                    member['icon'] = icon
                self.save_members()
                self.refresh_table()
                return

        self.members.append({"id": _id, "name": name, "icon": icon})
        self.save_members()
        self.refresh_table()

        # 清空输入框
        self.id_input.clear()
        self.name_input.clear()
        self.icon_input.clear()

        QMessageBox.information(self, "成功", f"成员 '{name}' 已添加！")

    def del_member(self):
        # 添加新成员，检查ID重复
        _id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        icon = self.icon_input.text().strip()

        # 修改成员
        for member in self.members:
            if member['id'] == _id:
                self.members.remove(member)
                self.save_members()
                self.refresh_table()
                QMessageBox.information(self, "成功", f"成员 '{name}' 已删除！")
                return

        QMessageBox.information(self, "删失败", f"成员 '{name}' 不存在！")

    def refresh_table(self):
        # 刷新表格显示
        self.table.setRowCount(len(self.members))
        for row, member in enumerate(self.members):
            self.table.setItem(row, 0, QTableWidgetItem(member['id']))
            self.table.setItem(row, 1, QTableWidgetItem(member['name']))
            self.table.setItem(row, 2, QTableWidgetItem(member['icon']))

    def browse_icon(self):
        # 打开文件对话框选择头像
        path, _ = QFileDialog.getOpenFileName(
            self, "选择头像图片", "", "图像文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.icon_input.setText(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemberManager()
    window.show()
    sys.exit(app.exec())

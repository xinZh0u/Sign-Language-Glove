from devicewidget import *
from datasaver import *

class RecordWidget(QWidget):
    record_buf = []
    current_path = ""
    current_name = ""
    ds = datasaver()
    cut_start = -1
    cut_end = -1
    record_flag = False
    mode = 0
    play_flag = False
    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,1000,600)
        layout = QVBoxLayout(self)
        self.dev_manager = DeviceManager()
        layout.addWidget(self.dev_manager)
        
        # 第一行
        layout_h1 = QHBoxLayout()
        layout.addLayout(layout_h1)
        
        self.label_name = QLabel("文件名")
        self.line_edit_name = QLineEdit()
        self.line_edit_name.textChanged.connect(self.change_path)
        self.label_path = QLabel("保存路径")
        self.line_edit_path = QLineEdit()
        self.line_edit_path.textChanged.connect(self.change_path)
        self.btn_path_select = QPushButton("浏览文件夹")
        self.btn_path_select.clicked.connect(self.browse_dir)
        self.btn_save_rec = QPushButton("保存")
        self.btn_save_rec.clicked.connect(self.record_save)
        
        layout_h1.addWidget(self.label_name)
        layout_h1.addWidget(self.line_edit_name)
        layout_h1.addWidget(self.label_path)
        layout_h1.addWidget(self.line_edit_path)
        layout_h1.addWidget(self.btn_path_select)
        layout_h1.addWidget(self.btn_save_rec)
        
        # 第二行
        layout_h2 = QHBoxLayout()
        layout.addLayout(layout_h2)
        
        self.label_buf_size = QLabel("数据长度:")
        
        self.label_start = QLabel("起始位置")
        self.slider_start = QSlider(Qt.Orientation.Horizontal)
        self.slider_start.valueChanged.connect(self.slider_start_change)
        self.label_end = QLabel("结束位置")
        self.slider_end = QSlider(Qt.Orientation.Horizontal)
        self.slider_end.valueChanged.connect(self.slider_end_change)
        self.btn_mode_switch = QPushButton("实时模式")   
        self.btn_mode_switch.clicked.connect(self.mode_switch)
        
        self.btn_play_auto = QPushButton("播放")   
        self.btn_play_auto.clicked.connect(self.play_auto)

        self.btn_start_rec = QPushButton("开始录制")   
        self.btn_start_rec.clicked.connect(self.record_start)
        self.btn_stop_rec = QPushButton("结束录制")
        self.btn_stop_rec.clicked.connect(self.record_end)
        layout_h2.addWidget(self.label_buf_size)
        layout_h2.addWidget(self.label_start)
        layout_h2.addWidget(self.slider_start)
        layout_h2.addWidget(self.label_end)
        layout_h2.addWidget(self.slider_end)
        layout_h2.addWidget(self.btn_mode_switch)
        layout_h2.addWidget(self.btn_play_auto)
        layout_h2.addWidget(self.btn_start_rec)
        layout_h2.addWidget(self.btn_stop_rec)
        
        self.slider_change()   
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_timeout) 
        self.timer.start(100)
        
    def browse_dir(self):
        # 打开文件对话框选择文件
        path = QFileDialog.getExistingDirectory(
            self, "选择目录","", QFileDialog.Options() 
        )
        
        if path:
            self.line_edit_path.setText(path)
    def change_path(self):
        print("改变目录")
        if self.line_edit_name.text() != self.current_name:
            self.record_buf.clear()
        if self.line_edit_path.text() != self.current_path:
            self.record_buf.clear()
        self.current_name = self.line_edit_name.text()
        self.current_path = self.line_edit_path.text()
        
        if self.current_name=="" or self.change_path == "":
            return
        name = self.current_path +'/'+ self.current_name
        
        if self.ds.set_file_path(name):
            self.record_buf = self.ds.get_buf()
        else:
            self.record_buf.clear()
            
        self.cut_end = -1
        self.cut_start = -1
        lenth = len(self.record_buf) 
        self.slider_start.setValue(0)            
        self.slider_end.setValue(lenth)    
        self.slider_change()
        
    def mode_switch(self):
        if self.mode == 0:
            self.mode = 1
            self.btn_mode_switch.setText("回放模式")
        elif self.mode == 1:
            self.mode = 0
            self.btn_mode_switch.setText("实时模式")
            
        
    def record_start(self):
        print("开始录制")
        self.record_buf.clear()
        self.record_flag =True
        
    def record_end(self):
        print("结束录制")
        self.record_flag = False
    
    def record_save(self):
        start = 0
        end = len(self.record_buf)
        if self.cut_end > 0:
            end = self.cut_end
            #self.record_buf = self.record_buf[:self.cut_end]
        if self.cut_start > 0:
            start = self.cut_start
        if self.cut_start > self.cut_end or self.cut_end>len(self.record_buf):
            print("保存失败")
            #self.record_buf = self.record_buf[self.cut_start:]
        self.ds.clear_lines()
        for line in self.record_buf[start:end]:
            self.ds.new_line_nums(line)
        self.ds.print_file()
        print(len(self.record_buf[start:end]))
            
    def record_replay(self,pos):
        self.dev_manager.rotate(self.record_buf[pos])
    
    def slider_change(self):
        start_value = self.slider_start.value()
        self.label_start.setText(f"起始位置:{start_value}")
        self.cut_start = start_value
        if self.mode == 1:
            self.record_replay(start_value)
        
        end_value = self.slider_end.value()
        self.label_end.setText(f"结束位置:{end_value}")
        self.cut_end = end_value
            
        lenth = len(self.record_buf)
        self.label_buf_size.setText(f"数据长度:{lenth}")
        if lenth > 0:
            self.slider_start.setMaximum(lenth-1)
            self.slider_end.setMaximum(lenth-1)
    
    def slider_start_change(self):  
        self.slider_change() 
        if self.mode == 1:
            self.record_replay(self.cut_start)      
            
    def slider_end_change(self):  
        self.slider_change() 
        if self.mode == 1:
            self.record_replay(self.cut_end)  
            
    def process_message(self,message):
        if self.mode == 0:
            self.dev_manager.process_rotate_message(message)
        if self.record_flag:
            mes = [float(num) for num in message.split(',')]
            self.record_buf.append(mes)
            
            lenth = len(self.record_buf)
            self.slider_end.setValue(lenth)     
            self.slider_change()   
    
    def play_auto(self):
        self.play_pos = self.cut_start
        self.play_flag = True

    def play_timeout(self):
        if self.play_flag == False:
            return
        if self.play_pos > self.cut_end:
            self.play_flag = False    
        
        self.mode = 1
        self.btn_mode_switch.setText("回放模式")
        if self.play_pos > 0 and self.play_pos < len(self.record_buf): 
            self.dev_manager.rotate(self.record_buf[self.play_pos])
            
        self.play_pos += 1
        print(self.play_pos)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecordWidget()
    window.show()
    sys.exit(app.exec())
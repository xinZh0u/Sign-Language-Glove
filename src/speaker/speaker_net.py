
import pyttsx3
import os
import threading
import time
import socket

running_flag = False

def speak_chinese_async(text, rate=160, volume=1.0):
    def _speak_task():
        global running_flag
        running_flag = True
        # try:
        #     # 初始化语音引擎
        #     engine = pyttsx3.init()
            
        #     # 设置语速和音量
        #     engine.setProperty('rate', rate)
        #     engine.setProperty('volume', volume)
            
        #     # 获取所有可用语音并查找中文语音
        #     voices = engine.getProperty('voices')
        #     chinese_voice_id = None
        #     for voice in voices:
        #         # 匹配包含 'chinese' 或 'zh' 标识的语音
        #         if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
        #             chinese_voice_id = voice.id
        #             break
            
            
        #     # 如果找到中文语音则设置，否则使用默认（可能发音不准）
        #     if chinese_voice_id:
        #         engine.setProperty('voice', chinese_voice_id)
        #     else:
        #         print("警告：未检测到明确的中文语音包，将使用系统默认语音。")
                
        #     # 执行朗读
        #     engine.say(text)
        #     engine.runAndWait()
        #     running_flag = False
            
        # except Exception as e:
        #     print(f"语音播放出错: {e}")
        
        try:
            os.system(f"espeak -v zh {text}")
            print(f"espeak -v zh {text}")
        except  Exception as e:
            print(f"语音播放出错: {e}")
        
    # 创建并启动守护线程
    thread = threading.Thread(target=_speak_task, daemon=True)
    thread.start()

local_ip = "127.0.0.1"
local_port = 7750

class speaker:
    
    queue = []
    
    def __init__(self,ip,port):
        super().__init__()
        self.ip = ip
        self.port = port

    def start(self):
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start() 
        self.queue_thread = threading.Thread(target=self._queue_loop, daemon=True)
        self.queue_thread.start()
    
    def _queue_loop(self):
        global running_flag
        while True:
            if running_flag == False:
                if self.queue!=[]:
                    speak_chinese_async(self.queue[0])    
                    self.queue = self.queue[1:]
            # print(running_flag)
            # print(self.queue)
            time.sleep(0.1)
        
    def _listen_loop(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip,self.port)
        server_socket.bind(server_address)
        print("UDP Server is listening...")
        while True:
            # 接受数据
            data, client_address = server_socket.recvfrom(1024)
            print(f"Received: {data.decode()} from {client_address}")
            self.queue.append(data.decode())
            # 发声
            os.system(f"espeak -v zh {data.decode()}")
        
s = speaker(local_ip,local_port)
s.start()
while True:
    pass
import os
import math
import numpy as np
import threading
import socket
from PySide6.QtCore import *

class wifi(QThread):
    get_message = Signal(str)

    def __init__(self,ip,port):
        super().__init__()
        self.ip = ip
        self.port = port

    def run(self):
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread.join(timeout=2)
        self.server_socket.close()

    def _listen_loop(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.ip,self.port)
        server_socket.bind(server_address)
        print("UDP Server is listening...")
        while True:
            # 接受数据
            data, client_address = server_socket.recvfrom(1024)
            print(f"Received: {data.decode()} from {client_address}")
            self.get_message.emit(data.decode())

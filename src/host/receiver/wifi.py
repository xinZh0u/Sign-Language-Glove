import signal
import os
import socket
import threading

class wifi:
    address = None
    data = None
    def __init__(self,ip,port,pid):
        self.ip = ip
        self.port = port
        self.pid = pid

    def start(self):
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
            self.data = data
            self.address = client_address
            self.update = 1
            os.kill(self.pid, signal.SIGUSR1)

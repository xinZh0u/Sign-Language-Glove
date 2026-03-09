# This Python file uses the following encoding: utf-8
import os
import math
import numpy as np
import asyncio
import time
import traceback
from bleak import BleakScanner
from bleak import BleakClient
from PySide6.QtCore import *

left  = 0
right = 1

async def scan():
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)

class BLE(QThread):
    global left
    global right

    leftStatus = Signal(int)
    leftReceive = Signal(str)

    rightStatus = Signal(int)
    rightReceive = Signal(str)

    def init(self,left_address,right_address,uuid):
        self.left_address = left_address
        self.right_address = right_address
        self.uuid = uuid

    async def connect(self,hand,address,uuid):
        while True:
            try:
                async with BleakClient(address) as client:
                    while True:
                        try:
                            model_number = await client.read_gatt_char(uuid)
                            data = model_number.decode()
                            #pak = [float(num) for num in data.split(',')]
                            if hand == left:
                                self.leftReceive.emit(data)
                                self.leftStatus.emit(1)
                            if hand == right:
                                self.rightReceive.emit(data)
                                self.rightStatus.emit(1)
                        except BleakError as e:
                            # 捕获BLE相关特定错误（如断开连接）
                            print(f"BLE错误: {e}，尝试重新连接...")
                            traceback.print_exc()
                            if hand == left:
                                self.leftStatus.emit(0)
                            if hand == right:
                                self.rightStatus.emit(0)
                            break  # 跳出内层循环进入外层重连
            except Exception as e:
                # 连接建立阶段发生的错误
                print(f"连接失败: {e}，正在重连...")
                self.leftStatus.emit(0)
                #await asyncio.sleep(1)


    def run(self):
        asyncio.run(self.connect(left,self.left_address,self.uuid))
        asyncio.run(self.connect(right,self.right_address,self.uuid))


# This Python file uses the following encoding: utf-8
import os
import math
import numpy as np
import asyncio
import time
from bleak import BleakScanner
from bleak import BleakClient


async def connect(pak,address,uuid):
    async with BleakClient(address) as client:
        while True:
            model_number = await client.read_gatt_char(uuid)
            data = model_number.decode()
            pak = [float(num) for num in data.split(',')]
            print(data)

async def scan():
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)

class BLE:
    pak = []
    def __init__(self,left_address,right_address,uuid):
        asyncio.run(connect(self.pak,left_address,uuid))

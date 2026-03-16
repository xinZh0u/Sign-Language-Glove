# This Python file uses the following encoding: utf-8
import os
import math
import numpy as np
import asyncio
import time
import traceback
from PySide6.QtCore import *

class mpipe(QThread):
    FIFO = []

    def init(self,name):
        self.name = name

    def send(self,message):
        self.FIFO.append(message)

    async def send_message(self,message):
        with open(self.name, 'w') as f:
            f.write(message)
        print(f"写入完成: {message}")

    async def task(self):
        while True:
            if self.FIFO != []:
                await self.send_message(self.FIFO[0])
                self.FIFO = self.FIFO[1:]

    async def run_both(self):
        left_task = asyncio.create_task(self.task())
        await asyncio.gather(left_task)

    def run(self):
        asyncio.run(self.run_both())

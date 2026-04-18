import math
import time
import sys
import signal
import threading
from wifi import *
from enum import Enum , auto
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

#local_ip = "localhost"
local_ip = "10.247.7.47"
local_port = 4321

# 设备ID枚举
class Dev(Enum):
  CENTER  = 0
  L_BIG   = auto()
  L_SMALL = auto()
  L_GLOVE = auto()
  R_BIG   = auto()
  R_SMALL = auto()
  R_GLOVE = auto()
  NUM = auto()
DEV = Dev    
  
# 包数据格式枚举    
class Pak(Enum):
  DEV   = auto()
  BTN   = auto()
  ROLL  = auto()
  PITCH = auto()
  YAW   = auto()
  FINGER_THUMB  = auto()
  FINGER_INDEX  = auto()
  FINGER_MIDDLE = auto()
  FINGER_RING   = auto()
  FINGER_LITTLE = auto()
  NUM = auto()
PAK = Pak

class BoneInfo(Enum):
  # 关节ID枚举
  #SHOULDER_CENTER = 0
  
  L_SHOULDER  = 0 #auto()
  L_ELBOW     = auto()
  L_WRIST     = auto()
  L_THUMB     = auto()
  L_INDEX     = auto()
  L_MIDDLE    = auto()
  L_RING      = auto()
  L_LITTLE    = auto()
  
  R_SHOULDER  = auto()
  R_ELBOW     = auto()
  R_WRIST     = auto()
  R_THUMB     = auto()
  R_INDEX     = auto()
  R_MIDDLE    = auto()
  R_RING      = auto()
  R_LITTLE    = auto()
  
  NUM = auto()  
  
  #(BEND,ROTATE)
  BEND = 0
  ROTATE = 1   
BONEINFO = BoneInfo

# 追踪器掉线超时时间    
update_timeout=1000    
    
class Tracker:
  online = 0
  last_update_time = 0
  pak = [0] * PAK.NUM.value
  
  pitch = 0 
  yaw   = 0 
  roll  = 0
  
  pitch_offset  = 0
  yaw_offset    = 0
  roll_offset   = 0
  
  def update(self,time,pak):
    print("update")
    self.last_update_time = time
    self.pak = pak
    self.pitch = pak[PAK.PITCH]-self.pitch_offset
    self.yaw = pak[PAK.YAW]-self.yaw_offset
    self.roll = pak[PAK.ROLL]-self.roll_offset

# 将陀螺仪数据解码为骨骼信息
class Decoder:
  
  # 网络
  address = None
  data = None
  ip   = local_ip
  port = local_port
  
  # 姿态追踪
  trackers = [Tracker()] * DEV.NUM.value
  bones = [[0,0]] * BONEINFO.NUM.value #骨骼数据，(角度，旋转)
  
  def __init__(self):
    print("Current Network",local_ip,local_port);

  def start(self):
    self.recv_th = threading.Thread(target=self._listen_loop, daemon=True)
    self.recv_th.start()
    self.calc_th = threading.Thread(target=self._calc_loop, daemon=True)
    self.calc_th.start()

  def stop(self):
    if self.recv_th:
      self.recv_th.join(timeout=2)
    self.server_socket.close()

  def _listen_loop(self):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (self.ip,self.port)
    server_socket.bind(server_address)
    print("UDP Server is listening...")
    while True:
      # 接收数据
      raw_data, client_address = server_socket.recvfrom(1024)
      data =raw_data.decode()
      print(f"Received: {data} from {client_address}")
      pak = [float(num) for num in data.split(',')]
      if len(pak) <5:
        continue
      id = int(pak[1]);
      self.trackers[pak[id]].update(time.time(),pak);
  
  def body_cali(self):
    for i,tra in enumerate(self.trackers):
      self.trackers[i].pitch_offset = self.trackers[i].pak[PAK.PITCH]
      self.trackers[i].yaw_offset   = self.trackers[i].pak[PAK.YAW]
      self.trackers[i].roll_offset  = self.trackers[i].pak[PAK.ROLL]
      
  # 输入两个追踪器，计算出骨骼数据并且赋值
  def bone_calc(self,tracker1,tracker2,bone_id):
    # 解算关节弯曲
    upper = [tracker1.pitch, tracker1.yaw, tracker1.roll]
    lower = [tracker2.pitch, tracker2.yaw, tracker2.roll] 
    a = lower[0] -upper[0]
    b = lower[1] - upper[1]
    bend = math.degrees(math.acos(math.cos(math.radians(a)) * math.cos(math.radians(b))))
    
    # 解算出关节旋转
    rotate = lower[2] -upper[2]
  
    #print(bend,rotate)
    self.bones[bone_id][BONEINFO.BEND.value] = bend;
    self.bones[bone_id][BONEINFO.ROTATE.value] = rotate;
    
  def _calc_loop(self):
    while True:
      # 判定设备是否在线 
      for i,tra in enumerate(self.trackers):
        offline_time = time.time() - tra.last_update_time
        if offline_time>=update_timeout:
          tra.online = False
          #print(f"Device {i} offline!")
        else:
          tra.online = True
             
      # 解算关节
      trk = self.trackers 
      # 左手
      self.bone_calc(trk[DEV.CENTER.value],trk[DEV.L_BIG.value],BONEINFO.L_SHOULDER.value)
      self.bone_calc(trk[DEV.L_BIG.value],trk[DEV.L_SMALL.value],BONEINFO.L_ELBOW.value)
      self.bone_calc(trk[DEV.L_SMALL.value],trk[DEV.L_GLOVE.value],BONEINFO.L_WRIST.value)
      self.bones[BONEINFO.L_THUMB.value] = trk[DEV.L_GLOVE.value].pak[PAK.FINGER_THUMB.value]
      self.bones[BONEINFO.L_INDEX.value] = trk[DEV.L_GLOVE.value].pak[PAK.FINGER_INDEX.value]
      self.bones[BONEINFO.L_MIDDLE.value] = trk[DEV.L_GLOVE.value].pak[PAK.FINGER_MIDDLE.value]
      self.bones[BONEINFO.L_RING.value] = trk[DEV.L_GLOVE.value].pak[PAK.FINGER_RING.value]
      self.bones[BONEINFO.L_LITTLE.value] = trk[DEV.L_GLOVE.value].pak[PAK.FINGER_LITTLE.value]
      
      # 右手
      self.bone_calc(trk[DEV.CENTER.value],trk[DEV.R_BIG.value],BONEINFO.R_SHOULDER.value)
      self.bone_calc(trk[DEV.R_BIG.value],trk[DEV.R_SMALL.value],BONEINFO.R_ELBOW.value)
      self.bone_calc(trk[DEV.R_SMALL.value],trk[DEV.R_GLOVE.value],BONEINFO.R_WRIST.value)
      self.bones[BONEINFO.R_THUMB.value] = trk[DEV.R_GLOVE.value].pak[PAK.FINGER_THUMB.value]
      self.bones[BONEINFO.R_INDEX.value] = trk[DEV.R_GLOVE.value].pak[PAK.FINGER_INDEX.value]
      self.bones[BONEINFO.R_MIDDLE.value] = trk[DEV.R_GLOVE.value].pak[PAK.FINGER_MIDDLE.value]
      self.bones[BONEINFO.R_RING.value] = trk[DEV.R_GLOVE.value].pak[PAK.FINGER_RING.value]
      self.bones[BONEINFO.R_LITTLE.value] = trk[DEV.R_GLOVE.value].pak[PAK.FINGER_LITTLE.value]
      
      time.sleep(0.01)

signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGUSR1})
if __name__ == "__main__":
  dec = Decoder()
  dec.start()
  
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    sys.exit(0)
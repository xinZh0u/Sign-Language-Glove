import bpy
import os 
import math
import numpy as np
import mathutils
import asyncio
import time
from bleak import BleakScanner
from bleak import BleakClient
from enum import Enum    
from multiprocessing import Process, Pipe

class PAK_E(Enum):
    TIME = 0
    POS_X = 1
    POS_Y = 2
    POS_Z = 3
    FINGER_THUMB  = 4
    FINGER_INDEX  = 5
    FINGER_MIDDLE = 6
    FINGER_RING   = 7
    FINGER_LITTLE = 8

hand_name_left = "J_Bip_L_Hand"

bone_name_left = [["J_Bip_L_Thumb1","J_Bip_L_Thumb2","J_Bip_L_Thumb3"],
            ["J_Bip_L_Index1","J_Bip_L_Index2","J_Bip_L_Index3"],
            ["J_Bip_L_Middle1","J_Bip_L_Middle2","J_Bip_L_Middle3"],
            ["J_Bip_L_Ring1","J_Bip_L_Ring2","J_Bip_L_Ring3"],
            ["J_Bip_L_Little1","J_Bip_L_Little2","J_Bip_L_Little3"]]

hand_name_right = "J_Bip_R_Hand"

bone_name_right = [["J_Bip_R_Thumb1","J_Bip_R_Thumb2","J_Bip_R_Thumb3"],
            ["J_Bip_R_Index1","J_Bip_R_Index2","J_Bip_R_Index3"],
            ["J_Bip_R_Middle1","J_Bip_R_Middle2","J_Bip_R_Middle3"],
            ["J_Bip_R_Ring1","J_Bip_R_Ring2","J_Bip_R_Ring3"],
            ["J_Bip_R_Little1","J_Bip_R_Little2","J_Bip_R_Little3"]]

# 进入姿态模式
bpy.ops.object.mode_set(mode='POSE')

bones = bpy.context.object.pose.bones

def bone_rotate(name,angle):
    global bones
    pose_bone = bones[name]
    pose_bone.rotation_mode = 'XYZ'
    pose_bone.rotation_euler = angle

def finger_rotate(finger,hand,angle):
    global bone_name_left
    global bone_name_right
    global bones
    
    bf = []
    if hand == 0:
        bf = bone_name_left
    else:
        bf = bone_name_right 
    
    for name in bf[finger]:
        bone_rotate(name,angle)
    
def wrist_rotate(hand,angle):
    global hand_name_left
    global hand_name_right
    if hand == 0:
        bone_rotate(hand_name_left,angle) 
    if hand == 1:
        bone_rotate(hand_name_right,angle) 
            
# 定义管道文件路径
PIPE_NAME = "/home/gzx/comu"

def receive_messages():
    # 从管道接收消息
    print("接收端启动，等待消息...")
    try:
        # 以只读方式打开管道
        while True:
            with open(PIPE_NAME, 'r') as pipe:
                line = pipe.readline()
                if line:
                    message = line.strip()
                    
                    if message == 'exit':
                        sys.exit(0)
                    
                    #转化数据包
                    hand = 0
                    if message[0] == 'L':
                        hand = 0
                    elif message[0] == 'R':
                        hand = 1
                    
                    message = message[1:]
                    pak = [float(num) for num in message.split(',')]
                    
                    # 调整腕关节姿态
                    euler = mathutils.Euler((math.radians(0), math.radians(0), math.radians(0)),'XYZ')
                    wrist_rotate(hand,euler) 
                    
                    # 调整指关节姿态
                    for i, num in enumerate(pak):
                        if i>=4 and i<=8:
                            angle = 0
                            if hand == 0:
                                angle = -pak[i]
                            else:
                                angle = pak[i] 
                            euler = mathutils.Euler(
                            (math.radians(0), math.radians(0), math.radians(angle)), 'XYZ')
                            finger_rotate(i-4,hand,euler)  
                            
                    # 更新视图          
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                    
    except Exception as e:
        print(f"接收异常: {e}")

if __name__ == "__main__":
    receive_messages()
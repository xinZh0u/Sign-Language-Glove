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


class PAK_E(Enum):
    PAK_POS_X = 0,
    PAK_POS_Y = 1,
    PAK_POS_Z = 2,
    PAK_FINGER_1 = 3,
    PAK_FINGER_2 = 4,
    PAK_FINGER_3 = 5,
    PAK_FINGER_4 = 6,
    PAK_FINGER_5 = 7,

hand_name = "J_Bip_L_Hand"

bond_name = [["J_Bip_L_Thumb1","J_Bip_L_Thumb2","J_Bip_L_Thumb3"],
            ["J_Bip_L_Index1","J_Bip_L_Index2","J_Bip_L_Index3"],
            ["J_Bip_L_Middle1","J_Bip_L_Middle2","J_Bip_L_Middle3"],
            ["J_Bip_L_Ring1","J_Bip_L_Ring2","J_Bip_L_Ring3"],
            ["J_Bip_L_Little1","J_Bip_L_Little2","J_Bip_L_Little3"]]
    

# 打印日志
def log(message):
    print(message)  # 输出到控制台
    with open("./output.log", "w") as f:
        f.write(message + "\n")


# 进入姿态模式
bpy.ops.object.mode_set(mode='POSE')

bones = bpy.context.object.pose.bones

def bone_rotate(name,angle):
    global bones
    pose_bone = bones[name]
    pose_bone.rotation_mode = 'XYZ'
    pose_bone.rotation_euler = angle
    #print(f"name:{name} {angle}")
    # 更新视图
    #bpy.context.view_layer.update()

def finger_rotate(finger,angle):
    global bond_name
    global bones
    for name in bond_name[finger]:
        bone_rotate(name,angle)
    #bone_rotate(bond_name[finger][0],angle)
    

# 定义管道文件路径
PIPE_NAME = "/tmp/glove_pipe"

def receive_messages():
    """从管道接收消息"""
    print("接收端启动，等待消息...")
    try:
        # 以只读方式打开管道
        with open(PIPE_NAME, 'r') as pipe:
            while True:
                line = pipe.readline()
                if line:
                    message = line.strip()
                    print(f"接收: {message}")
                    pak = [float(num) for num in message.split(',')]
                    global hand_name
                    euler = mathutils.Euler((math.radians(0), math.radians(0), math.radians(0)),'XYZ')
                    bone_rotate(hand_name,euler) 
                    
                    for i, num in enumerate(pak):
                        if i>=3 and i<=7:
                            euler = mathutils.Euler(
                            (math.radians(0), math.radians(0), math.radians(-pak[i])), 'XYZ')
                            finger_rotate(i-3,euler)    
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                else:
                    time.sleep(0.01)  # 短暂休眠避免CPU占用过高
    except Exception as e:
        print(f"接收异常: {e}")
    finally:
        # 清理管道文件
        if os.path.exists(PIPE_NAME):
            os.remove(PIPE_NAME)
            print("管道文件已清理")

if __name__ == "__main__":
    receive_messages()

# This Python file uses the following encoding: utf-8
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
    PAK_TIME = 0,
    PAK_POS_X = 1,
    PAK_POS_Y = 2,
    PAK_POS_Z = 3,
    PAK_FINGER_1 = 4,
    PAK_FINGER_2 = 5,
    PAK_FINGER_3 = 6,
    PAK_FINGER_4 = 7,
    PAK_FINGER_5 = 8,

class model:
    def __init__(self,hand,handBones):
        # 进入姿态模式
        bpy.ops.object.mode_set(mode='POSE')
        self.handBones = handBones
        self.hand = hand

    def bone_rotate(name,angle):
        pose_bone = self.handBones[name]
        pose_bone.rotation_mode = 'XYZ'
        pose_bone.rotation_euler = angle

    def finger_rotate(finger,angle):
        for name in bond_name[finger]:
            self.bone_rotate(name,angle)

    def adjust(mixPak):
        pak = [float(num) for num in data.split(',')]

        euler = mathutils.Euler((math.radians(0), math.radians(0), math.radians(0)),'XYZ')
        self.bone_rotate(self.hand,euler)

        for i, num in enumerate(pak):
            if i>=4 and i<=8:
                euler = mathutils.Euler(
                    (math.radians(0), math.radians(0), math.radians(-pak[i])),
                    'XYZ')
                self.finger_rotate(i-4,euler)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

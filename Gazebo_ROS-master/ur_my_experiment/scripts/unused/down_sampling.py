#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity

#   20191216   Urakawa
#   zed で取った　PointCloud2 型　をダウンサンプリング

import rospy
import random,math
import numpy as np
import copy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg

from std_msgs.msg import Bool
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Vector3
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped

from sensor_msgs.msg import (   PointCloud2,
                                PointField)
import sensor_msgs.point_cloud2 as pc2

def down_sample(data,min,max):
    #data で 点群のリスト 縦３ × 横 N をもらう
    # 順番に処理していって　min より近くに点があらわれたらそれを削除
    # max より近くに点がなかったらそれも削除
    # 近くに点がある、もしくはある程度の距離以内に点がない場合に削除
    pass

def distance(x,y,z):
    return x*x+y*y+z*z

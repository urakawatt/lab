#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity

#   20191220    Urakawa
#   ur3_moveit .launch を実行したときに
#   camera_base  を tf listen してその位置に Zed の　base を設置する


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

import tf


 
class MakeTF:

    def __init__(self):
        rospy.init_node('tf_zedbase', anonymous=True)#ノードの初期化　reaching ていう名前
        self.set_ZEDbase()

    
    def set_ZEDbase(self):
        listener = tf.TransformListener()
        if rospy.is_shutdown():
            return
        listener.waitForTransform('world','camera_base',rospy.Time(0),rospy.Duration(2.0))
        (self.trans,rot)=listener.lookupTransform('/world','/camera_base',rospy.Time(0)) # trans(x,y,z) rot (x,y,z,w)
        if rospy.is_shutdown():
            return
        print('trans = '+str(self.trans))
        self.br = tf.TransformBroadcaster()
        self.br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),(0.0,0.0,0.0,1.0),rospy.Time.now(),'base_forZED','world')


    def Broadcast(self):
        if rospy.is_shutdown():
            return
        self.br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),(0.0,0.0,0.8509035,0.525322),rospy.Time.now(),'base_forZED','world')
        

        
       

if __name__ == '__main__':
    try:
        m = MakeTF()
        
        while not rospy.is_shutdown():
             m.Broadcast()
        
    except rospy.ROSInterruptException:
        pass

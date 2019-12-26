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

def quaternion_to_euler(quaternion):
    """Convert Quaternion to Euler Angles

    quarternion: geometry_msgs/Quaternion
    euler: geometry_msgs/Vector3
    """
    e = tf.transformations.euler_from_quaternion((quaternion[0], quaternion[1], quaternion[2], quaternion[3]))
    return [e[0], e[1], e[2]]
 
def euler_to_quaternion(euler):
    """Convert Euler Angles to Quaternion

    euler: geometry_msgs/Vector3
    quaternion: geometry_msgs/Quaternion
    """
    q = tf.transformations.quaternion_from_euler(euler[0], euler[1], euler[2])
    return [q[0], q[1], q[2], q[3]]


class MakeTF:

    def __init__(self):
        rospy.init_node('tf_zedbase', anonymous=True)#ノードの初期化　reaching ていう名前
        self.set_ZEDbase()

    
    def set_ZEDbase(self):
        listener = tf.TransformListener()
        if rospy.is_shutdown():
            return
        listener.waitForTransform('world','camera_base',rospy.Time(0),rospy.Duration(2.0))
        (self.trans,self.rot)=listener.lookupTransform('/world','/camera_base',rospy.Time(0)) # trans(x,y,z) rot (x,y,z,w)
        # x,y 平面は world のxy平面　と平行にしたいけど　z 軸回転はそのまま残したいので　roll pitch yaw に変換して yaw だけ残してほかは０にする
        self.rot = euler_to_quaternion((0,0,quaternion_to_euler(self.rot)[2]))

        if rospy.is_shutdown():
            return
        
        
        print('trans = '+str(self.trans))
        self.br = tf.TransformBroadcaster()
        self.br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),self.rot,rospy.Time.now(),'map','world')


    def Broadcast(self):
        if rospy.is_shutdown():
            return
        self.br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),self.rot,rospy.Time.now(),'map','world')
        

        
       

if __name__ == '__main__':
    try:
        m = MakeTF()
        
        while not rospy.is_shutdown():
             m.Broadcast()
        
    except rospy.ROSInterruptException:
        pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   20191217    Urakawa
#   zed のための base の tf を配信してあげる
import rospy
import random,math
import numpy as np
import copy
import tf


def set_basetf():#ee_link のっ場所に回転なしの tf を設置
    #rospy.init_node('tf_node_zed')
    listener = tf.TransformListener()

    (trans,rot)=listener.lookupTransform('/world','/camera_base',rospy.Time(0)) # trans(x,y,z) rot (x,y,z,w)
    
    br = tf.TransformBroadcaster()
    br.sendTransform(trans,(0,0,0,1),rlink>

    <joint name="${prefix}shoulder_pan_joint" type="revolute">
      <parent link="${prefix}base_link" />
      <child link = "${prefix}shoulder_link" />
      <origin xyz="0.0 0.0 ${shoulder_height}" rpy="0.0 0.0 0.0" />ospy.Time.now(),'base_forZED','world')

if __name__ == '__main__':

    rospy.init_node('set_base_forZED', anonymous=True)
    listener = tf.TransformListener()
    listener.waitForTransform('world','ee_link',rospy.Time(0),rospy.Duration(2.0))

    (trans,rot)=listener.lookupTransform('/world','/ee_link',rospy.Time(0)) # trans(x,y,z) rot (x,y,z,w)
    
    br = tf.TransformBroadcaster()
    try:
        print('aaaaa')
        while not rospy.is_shutdown(): 
            br.sendTransform(trans,(0,0,0,1),rospy.Time.now(),'base_forZED','world')

        
    except rospy.ROSInterruptException:
        pass

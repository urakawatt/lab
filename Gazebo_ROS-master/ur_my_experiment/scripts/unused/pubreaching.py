#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity

#   20190725    Urakawa
#   指定したトピックを購読させて、トピック越しに操作する　配信者
import rospy
import random,math
import numpy as np
import copy
from moveit_python import (MoveGroupInterface,
                           PlanningSceneInterface,
                           PickPlaceInterface)
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from geometry_msgs.msg import Vector3
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped


def talker():
    pub=rospy.Publisher("/UR/reaching/pose",Vector3,queue_size=10)
    rospy.init_node('Pubreach',anonymous=True)
    inx,iny,inz=raw_input('x y z: ').split()
    print inx +' '+ iny +' '+ inz
    r=rospy.Rate(1)
    while not rospy.is_shutdown():      #ループ処理
        reachPose=Vector3()
        reachPose.x=float(inx)
        reachPose.y=float(iny)
        reachPose.z=float(inz)

        pub.publish(reachPose)
        r.sleep()

            
if __name__ == '__main__':
    try:
        talker()              
    except rospy.ROSInterruptException:
        pass

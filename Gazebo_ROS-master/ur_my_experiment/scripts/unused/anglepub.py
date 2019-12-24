#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity

#   20190909   Urakawa
#   moveit の
import rospy
import random,math
import numpy as np
import copy
import tf
from moveit_python import (MoveGroupInterface,
                           PlanningSceneInterface,
                           PickPlaceInterface)
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Vector3
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Quaternion
from sensor_msgs.msg import JointState


class PublishAngle:
    def __init__(self):
        self.init_publisher()
 
    def init_publisher(self):
        self.pub0=rospy.Publisher("/unity/ur3/joint_states/elbow_joint",PoseStamped,queue_size=10)
        self.pub1=rospy.Publisher("/unity/ur3/joint_states/shoulder_lift_joint",PoseStamped,queue_size=10)
        self.pub2=rospy.Publisher("/unity/ur3/joint_states/shoulder_pan_joint",PoseStamped,queue_size=10)
        self.pub3=rospy.Publisher("/unity/ur3/joint_states/wrist_1_joint",PoseStamped,queue_size=10)
        self.pub4=rospy.Publisher("/unity/ur3/joint_states/wrist_2_joint",PoseStamped,queue_size=10)
        self.pub5=rospy.Publisher("/unity/ur3/joint_states/wrist_3_joint",PoseStamped,queue_size=10)
        self.angle0=0
        self.angle1 = 0
        self.angle2 = 0
        self.angle3 = 0
        self.angle4 = 0
        self.angle5 = 0

        rospy.init_node('Pubangle',anonymous=True)

    def start_subscriber(self):     #購読をスタート
        rospy.Subscriber("/joint_states",JointState, self.callback)    
    
    def callback(self,data):#多分データはラジアンできてる
        print "callbacked"
        self.angle0 = data.position[0]   #elbow joint
        self.angle1 = data.position[1]   #shoulder lift joint    Z
        self.angle2 = data.position[2]   #shoulder pan joint     Z
        self.angle3 = data.position[3]   #wrist 1 joint          Z
        self.angle4 = data.position[4]   #wrist 2 joint          Z
        self.angle5 = data.position[5]   #wrist 3 joint          Z
        print "jointstates"+data
        

    def euler_to_quaternion(self,euler):
        """Convert Euler Angles to Quaternion

        euler: geometry_msgs/Vector3
        quaternion: geometry_msgs/Quaternion
        """
        q = tf.transformations.quaternion_from_euler(euler.x, euler.y, euler.z)
        return Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])

    def set_angle(self,angle):
        self.data=PoseStamped()
        self.data.pose.position=Vector3(0.0,0.0,0.0)
        self.data.pose.orientation = self.euler_to_quaternion(Vector3(0.0,0.0,angle*math.pi/180))
        return self.data

    def start_publish(self):
        while not rospy.is_shutdown():  
           #ループ処理
           self.start_subscriber()
           if self.angle0 is not None:
                print "publishing now!!"
                self.pub0.publish(self.set_angle(self.angle0))
                self.pub1.publish(self.set_angle(self.angle1))
                self.pub2.publish(self.set_angle(self.angle2))
                self.pub3.publish(self.set_angle(self.angle3))
                self.pub4.publish(self.set_angle(self.angle4))
                self.pub5.publish(self.set_angle(self.angle5))
        
    
    

if __name__ == '__main__':

    try:
        p=PublishAngle()
        p.start_publish()

        
    except rospy.ROSInterruptException:
        pass

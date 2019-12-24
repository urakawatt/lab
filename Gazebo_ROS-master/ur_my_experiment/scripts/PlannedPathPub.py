#!/usr/bin/env python
# -*- coding: utf-8 -*-


#   20191205  Urakawa
#　 /move_group/display_planned_path  に
#   ur3_moveit.launch でmoveit してるときに 実行前のplanning のときのjointstates の変化が配信されてる
#   これをfloat32multiarray 型を使ってunityに送る （topic を配信する
#   
#   shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint,wrist_3_joint
#   横６　×　縦  N
#   横にひっつけて１次元配列でおくる
#    向こうで２次元配列にする

import rospy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import PoseStamped
import moveit_msgs.msg
from moveit_msgs.msg import(RobotTrajectory, DisplayTrajectory)
from trajectory_msgs.msg import(JointTrajectory,JointTrajectoryPoint)

def callback(data):

    talker(data.trajectory[0].joint_trajectory.points)

def listener():
    
    rospy.init_node('PlannedPathPublisher',anonymous=True)
    rospy.Subscriber("/move_group/display_planned_path",DisplayTrajectory, callback)
    rospy.spin()


def talker(points):
    pub = rospy.Publisher('/unity/planned_path', Float32MultiArray, queue_size=10)

    array=[]

    i=0
    for data in points:
        for position in data.positions:
            #array.data[i]=position
            array.append(position)
            i+=1
            print(str(i)+'  =  '+ str(position))

    pubarray = Float32MultiArray(data=array)
    pub.publish(pubarray)



if __name__ == '__main__':
    listener()

    
    

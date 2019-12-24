#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
import random,math
import numpy as np


def joint_control():
    pub1 = rospy.Publisher('/simple_arm/joint1_position_controller/command', Float64, queue_size=10)
    pub2 = rospy.Publisher('/simple_arm/joint2_position_controller/command', Float64, queue_size=10)
    pub3 = rospy.Publisher('/simple_arm/joint3_position_controller/command', Float64, queue_size=10)
    pub4 = rospy.Publisher('/simple_arm/joint4_position_controller/command', Float64, queue_size=10)
    pub5 = rospy.Publisher('/simple_arm/joint5_position_controller/command', Float64, queue_size=10)
    pub6 = rospy.Publisher('/simple_arm/joint6_position_controller/command', Float64, queue_size=10)
    pub7 = rospy.Publisher('/simple_arm/joint7_position_controller/command', Float64, queue_size=10)
    rospy.init_node('joint_control', anonymous=True)
    
    rate = rospy.Rate(0.5)
    count = 0
    while not rospy.is_shutdown():
        #v = rospy.get_time()
        #rospy.loginfo(v)
        
        joint_pos = [random.uniform(-2.0,2.0), random.uniform(-1.0,1.0), random.uniform(-1.0,1.0), random.uniform(-1.0,1.0), random.uniform(-3.14,3.14)]

        pub1.publish(joint_pos[0])
        pub2.publish(joint_pos[1])
        pub3.publish(joint_pos[2])
        pub4.publish(joint_pos[3])
        pub5.publish(joint_pos[4])
        
        if count%2 == 0:
            pub6.publish(0.0)
            pub7.publish(0.0)
        else:
            pub6.publish(0.008)
            pub7.publish(0.008)

        count += 1
        rospy.loginfo("joint pose %s", joint_pos)
        rate.sleep()



if __name__ == '__main__':
    try:
        joint_control()   
    except rospy.ROSInterruptException:
        pass
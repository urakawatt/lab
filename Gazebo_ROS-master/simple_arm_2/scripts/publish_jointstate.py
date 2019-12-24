#!/usr/bin/env python
# license removed for brevity

import sys
import rospy
from sensor_msgs.msg import JointState

def node():
    rospy.init_node('publish_jointstate', anonymous=True)
    pub = rospy.Publisher('joint_states', JointState, queue_size=10)
    rate = rospy.Rate(100)
    
    while not rospy.is_shutdown():
        msg = JointState()
        msg.header.stamp = rospy.Time.now()
        msg.position = [ 0.0, -0.2, -0.2, -0.2, 0.0 ]
        msg.velocity = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
        msg.effort = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
        msg.name = ["joint1", "joint2", "joint3", "joint4", "joint5"]

        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        node()   
    except rospy.ROSInterruptException:
        pass
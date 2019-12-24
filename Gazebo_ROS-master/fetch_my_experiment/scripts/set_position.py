#!/usr/bin/env python
# license removed for brevity

import copy
import actionlib
import rospy

from moveit_python import (MoveGroupInterface,
                           PlanningSceneInterface,
                           PickPlaceInterface)
from control_msgs.msg import PointHeadAction, PointHeadGoal
from moveit_msgs.msg import PlaceLocation, MoveItErrorCodes, Grasp

def move():
	rospy.init_node("move")

	move_group = MoveGroupInterface("arm_with_torso", "base_link")

	#move head camera
	client = actionlib.SimpleActionClient("head_controller/point_head", PointHeadAction)
	rospy.loginfo("Waiting for head_controller...")
	client.wait_for_server()

	goal = PointHeadGoal()
	goal.target.header.stamp = rospy.Time.now()
	goal.target.header.frame_id = "base_link"
	goal.target.point.x = 1.5
	goal.target.point.y = 0.0
	goal.target.point.z = 0.0
	goal.min_duration = rospy.Duration(1.0)
	client.send_goal(goal)
	client.wait_for_result()



if __name__ == '__main__':
	move()
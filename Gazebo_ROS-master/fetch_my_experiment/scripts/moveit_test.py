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


	#planning scene setup
	planning_scene = PlanningSceneInterface("base_link")
	planning_scene.removeCollisionObject("my_front_ground")
	planning_scene.removeCollisionObject("my_back_ground")
	planning_scene.removeCollisionObject("my_right_ground")
	planning_scene.removeCollisionObject("my_left_ground")
	planning_scene.addCube("my_front_ground", 2, 1.1, 0.0, -1.0)
	planning_scene.addCube("my_back_ground", 2, -1.2, 0.0, -1.0)
	planning_scene.addCube("my_left_ground", 2, 0.0, 1.2, -1.0)
	planning_scene.addCube("my_right_ground", 2, 0.0, -1.2, -1.0)


	#move head camera
	client = actionlib.SimpleActionClient("head_controller/point_head", PointHeadAction)
	rospy.loginfo("Waiting for head_controller...")
	client.wait_for_server()

	goal = PointHeadGoal()
	goal.target.header.stamp = rospy.Time.now()
	goal.target.header.frame_id = "base_link"
	goal.target.point.x = 1.2
	goal.target.point.y = 0.0
	goal.target.point.z = 0.0
	goal.min_duration = rospy.Duration(1.0)
	client.send_goal(goal)
	client.wait_for_result()

	#arm setup
	move_group = MoveGroupInterface("arm", "base_link")
	#set arm initial position
	joints = ["shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
                  "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
	pose = [1.32, 0.7, 0.0, -2.0, 0.0, -0.57, 0.0]
	while not rospy.is_shutdown():
		result = move_group.moveToJointPosition(joints, pose, 0.02)
		if result.error_code.val == MoveItErrorCodes.SUCCESS:
			return
	




if __name__ == '__main__':
	move()
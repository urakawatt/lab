#!/usr/bin/env python
# license removed for brevity

import copy
import actionlib
import rospy

from math import sin, cos
from moveit_python import (MoveGroupInterface,
                           PlanningSceneInterface,
                           PickPlaceInterface)
from moveit_python.geometry import rotate_pose_msg_by_euler_angles

from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from control_msgs.msg import PointHeadAction, PointHeadGoal
from grasping_msgs.msg import FindGraspableObjectsAction, FindGraspableObjectsGoal
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from moveit_msgs.msg import PlaceLocation, MoveItErrorCodes, Grasp
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from gazebo_msgs.msg import ModelStates
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from visualization_msgs.msg import MarkerArray
import tf


class Reaching:
	def __init__(self):
		rospy.init_node('reaching', anonymous=True)
		self.model_pose = [0.0,0.0,0.0]

		self.set_init_pose()
		#self.set_forbidden()

	def set_forbidden(self):
		#set forbidden erea
		self.planning_scene = PlanningSceneInterface("base_link")
		self.planning_scene.removeCollisionObject("my_front_ground")
		self.planning_scene.removeCollisionObject("my_back_ground")
		self.planning_scene.removeCollisionObject("my_right_ground")
		self.planning_scene.removeCollisionObject("my_left_ground")
		self.planning_scene.addCube("my_front_ground", 2, 1.1, 0.0, -1.0)
		self.planning_scene.addCube("my_back_ground", 2, -1.2, 0.0, -1.0)
		self.planning_scene.addCube("my_left_ground", 2, 0.0, 1.2, -1.0)
		self.planning_scene.addCube("my_right_ground", 2, 0.0, -1.2, -1.0)
		self.planning_scene.removeCollisionObject("demo_cube")
    
	def set_init_pose(self): 
		#set init pose
		move_group = MoveGroupInterface("arm_with_torso", "base_link")
		#set arm initial position
		joints = ["torso_lift_joint", "shoulder_pan_joint",
					"shoulder_lift_joint", "upperarm_roll_joint",
					"elbow_flex_joint", "forearm_roll_joint",
					"wrist_flex_joint", "wrist_roll_joint"]
		#pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
		pose = [0.385, -1.0, -1.0, 0.0, 1.0, 0.0, 1.5, 0.0]
		#pose = [0.385, 1.32, 0.7, 0.0, -2.0, 0.0, -0.57, 0.0]
		result = move_group.moveToJointPosition(joints, pose, 0.02)

	def target(self):
		rate = rospy.Rate(1)
		rospy.sleep(1)
		ls = tf.TransformListener()
		while not rospy.is_shutdown():
			print self.model_pose

			try:
				(trans,rot) = ls.lookupTransform('/base_link', '/object', rospy.Time(0))
				print "tf base_link to test",trans
			
				group = moveit_commander.MoveGroupCommander("arm_with_torso")
				#print group.get_current_pose().pose
				pose_target = geometry_msgs.msg.Pose()
				pose = group.get_current_pose().pose
				pose_target = geometry_msgs.msg.Pose()
				pose_target.orientation.x = pose.orientation.x
				pose_target.orientation.y = pose.orientation.y
				pose_target.orientation.z = pose.orientation.z
				pose_target.orientation.w = pose.orientation.w
				pose_target.position.x = trans[0]
				pose_target.position.y = trans[1]
				pose_target.position.z = trans[2]+0.3

				group.set_pose_target(pose_target)
				group.go()

			except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
				print "e"

			rospy.sleep(1)




if __name__ == '__main__':
	r = Reaching()
	r.target()
	
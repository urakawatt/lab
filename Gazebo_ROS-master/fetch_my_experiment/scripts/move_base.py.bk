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

from geometry_msgs.msg import Twist
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from nav_msgs.msg import Odometry
import tf


class Move_Base:
	def __init__(self):
		rospy.init_node('move_base')
		self.model_pose1 = [0.0,0.0,0.0]
		self.model_pose2 = [0.0,0.0,0.0]
		self.robot_pose = [0.0,0.0]

		self.marker_pub = rospy.Publisher("visualization_marker_array", MarkerArray)
		self.start_subscriber()

		ls = tf.TransformListener()
		rate = rospy.Rate(10)
		while not rospy.is_shutdown():
			self.publish_marker()
			self.moving(1.0,0.0)
			self.publish_tf()

			# wondering, code below is not functioning when separatery as def function.
			try:
				(trans,rot) = ls.lookupTransform('/base_link', '/object', rospy.Time(0))
				print "tf base_link to test",trans
				(trans,rot) = ls.lookupTransform('/odom', '/object', rospy.Time(0))
				print "tf odom to test",trans
			except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
				print "e"

			rate.sleep()

	def callback1(self,data):
		x = data.pose[3].position.x
		y = data.pose[3].position.y
		z = data.pose[3].position.z
		self.model_pose1 = [x,y,z]

		x = data.pose[1].position.x
		y = data.pose[1].position.y
		z = data.pose[1].position.z
		self.model_pose2 = [x,y,z]

	def callback2(self,data):
		self.robot_pose = [data.pose.pose.position.x, data.pose.pose.position.y]
		#print "robot pose ",self.robot_pose

	def publish_marker(self):
		print "model_pose ",self.model_pose1
		markerArray = MarkerArray()
		marker = Marker()
		marker.header.frame_id = "/odom"
		marker.type = marker.SPHERE
		marker.action = marker.ADD
		marker.scale.x = 0.1
		marker.scale.y = 0.1
		marker.scale.z = 0.1
		marker.color.a = 1.0
		marker.color.r = 1.0
		marker.color.g = 1.0
		marker.color.b = 0.0
		marker.pose.orientation.w = 1.0
		marker.pose.position.x = self.model_pose1[0]
		marker.pose.position.y = self.model_pose1[1]
		marker.pose.position.z = self.model_pose1[2]
		markerArray.markers.append(marker)
		self.marker_pub.publish(markerArray)	

	def publish_tf(self):
		br = tf.TransformBroadcaster()
		br.sendTransform((self.model_pose1[0], self.model_pose1[1], self.model_pose1[2]), (0.0, 0.0, 0.0, 1.0), rospy.Time.now(), "object", "odom")

	def base_link_tf(self):
		ls = tf.TransformListener()
		rate = rospy.Rate(10.0)
		while not rospy.is_shutdown():
			try:
				(trans,rot) = ls.lookupTransform('/odom', 'base_link', rospy.Time(0))
				print "trans",trans
			except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
				print "e"

			rate.sleep()
		

	def start_subscriber(self):
		rospy.Subscriber("/gazebo/model_states", ModelStates, self.callback1)
		rospy.Subscriber("/odom", Odometry, self.callback2)

	def moving(self,target_x,target_y):
		cmd = rospy.Publisher("/base_controller/command", Twist)
		move_cmd = Twist()
		move_cmd.linear.x = target_x - self.robot_pose[0]
		move_cmd.linear.y = 0.0
		move_cmd.linear.z = 0.0
		move_cmd.angular.x = 0.0
		move_cmd.angular.y = 0.0
		move_cmd.angular.z = 0.0
		#probably fetch base controllable param is only linear.x and angular.z because fetch base have 2 wheels.

		cmd.publish(move_cmd)
		





if __name__ == '__main__':
	m = Move_Base()



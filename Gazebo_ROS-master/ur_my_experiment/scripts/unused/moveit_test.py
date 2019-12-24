#!/usr/bin/env python
# license removed for brevity
import rospy
import random,math
import numpy as np
import copy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from moveit_python import (MoveGroupInterface,
                           PlanningSceneInterface,
                           PickPlaceInterface)

def move():
    rospy.init_node("move")

    #
    #target pose
    #
    robot = moveit_commander.RobotCommander()
    print "group name  ",robot.get_group_names()
    #print "current state ",robot.get_current_state()
    group = moveit_commander.MoveGroupCommander("manipulator")

    group_initial_pose = group.get_current_pose().pose
    print "group initaial pose ",group_initial_pose

    pose_target = geometry_msgs.msg.Pose()
    pose_target.orientation.x = 0.0
    pose_target.orientation.y = 0.0
    pose_target.orientation.z = 0.0
    pose_target.orientation.w = 1.0
    pose_target.position.x = 0.5
    pose_target.position.y = 0.5
    pose_target.position.z = 0.9

    group.set_pose_target(pose_target)
    group.go()


    #
    #joint pose
    #
    move_group = MoveGroupInterface("manipulator","base_link")
    #planning_scene = PlanningSceneInterface("base_link")
    
    #setting up to initial robot state
    # TF joint names
    joint_names = ["shoulder_pan_joint", "shoulder_lift_joint",
                    "elbow_joint", "wrist_1_joint",
                    "wrist_2_joint", "wrist_3_joint"]
    # Lists of joint angles in the same order as in joint_names
    pose = [0.0, -1.98, 1.0, -0.64, -1.57, 0.0]
                   
    move_group.moveToJointPosition(joint_names, pose, wait=False)
    move_group.get_move_action().wait_for_result()
    result = move_group.get_move_action().get_result()
    move_group.get_move_action().cancel_all_goals()


    #
    #cartesian path
    #
    #moveing along with catesian paths
    group = moveit_commander.MoveGroupCommander("manipulator")
    waypoints = []
    
    # start with the current pose
    waypoints.append(group.get_current_pose().pose)

    # first orient gripper and move
    wpose = geometry_msgs.msg.Pose()
    wpose.orientation.w = 1.0
    wpose.position.x = waypoints[0].position.x 
    wpose.position.y = waypoints[0].position.y
    wpose.position.z = waypoints[0].position.z - 0.05
    waypoints.append(copy.deepcopy(wpose))

    # second move
    wpose.position.x += 0.03
    waypoints.append(copy.deepcopy(wpose))

    (plan, fraction) = group.compute_cartesian_path(waypoints,0.01,0.0) #waypoints to follow, eef_setup, jump_threshold
    group.execute(plan)



if __name__ == '__main__':
    try:
        move()
        
    except rospy.ROSInterruptException:
        pass
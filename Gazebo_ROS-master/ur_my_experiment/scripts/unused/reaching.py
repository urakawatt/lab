#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity
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
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped


class Reaching:
    def __init__(self):
        rospy.init_node('reaching', anonymous=True)#ノードの初期化　reaching ていう名前
        self.robot = moveit_commander.RobotCommander()# インスタンスの作成
        self.model_pose = [0.0,0.0,0.0]     #モデルの姿勢
        self.obstacle_pose = [0.0,0.0,0.0]  #障害物の位置
        self.set_forbidden()    #禁止エリアの初期化
        self.set_init_pose()    #位置姿勢の初期化

    def set_forbidden(self):
        #set forbidden erea
        self.planning_scene = PlanningSceneInterface("base_link")   #PlanningSceneInterface のインスタンスの作成

        self.planning_scene.removeCollisionObject("my_front_ground")
        self.planning_scene.removeCollisionObject("my_back_ground")
        self.planning_scene.removeCollisionObject("my_right_ground")
        self.planning_scene.removeCollisionObject("my_left_ground")     #オブジェクトの削除
        self.planning_scene.addCube("my_front_ground", 2, 1.1, 0, -1.0)
        self.planning_scene.addCube("my_back_ground", 2, -1.2, 0, -1.0)
        self.planning_scene.addCube("my_left_ground", 2, 0.0, 1.0, -1.0)
        self.planning_scene.addCube("my_right_ground", 2, 0.0, -1.0, -1.0) #座標に立方体を挿入 
        self.planning_scene.removeCollisionObject("demo_cube") 
        self.planning_scene.removeCollisionObject("obstacle")       #オブジェクトの削除
        print dir(self.planning_scene)  #インスタンス内のあらゆるオブジェクトの属性とメソッドのリストを表示
        import inspect
        print "addBox's variable is ",inspect.getargspec(self.planning_scene.addBox)
        print "attachBox's variable is ",inspect.getargspec(self.planning_scene.attachBox)
        print "addCube's variable is ",inspect.getargspec(self.planning_scene.addCube)
        print "setColor's variable is ",inspect.getargspec(self.planning_scene.setColor)		#python関数のパラメータの名前とデフォルト値を取得

    def set_init_pose(self): 
        #set init pose　
        move_group = MoveGroupInterface("manipulator","base_link")	#MoveGroupInterface のインスタンスの作成
        planning_scene = PlanningSceneInterface("base_link")		#PlanningSceneInterface のインスタンスの作成
        joint_names = ["shoulder_pan_joint", "shoulder_lift_joint",		#ジョイントの名前を定義
                        "elbow_joint", "wrist_1_joint",
                        "wrist_2_joint", "wrist_3_joint"]
        pose = [0.0, -1.98, 1.0, -0.64, -1.57, 0.0]
        move_group.moveToJointPosition(joint_names, pose, wait=False)#joint_names を pose に動かす
        move_group.get_move_action().wait_for_result()      #wait result
        result = move_group.get_move_action().get_result()  #result を代入
        move_group.get_move_action().cancel_all_goals()     #すべてのゴールをキャンセル


    def callback(self,data):    #トピックにデータが追加されるたびに呼ばれる
        x = data.pose[1].position.x
        y = data.pose[1].position.y
        z = data.pose[1].position.z
        self.model_pose = [x,y,z]       #modelの姿勢を代入
        
        x = data.pose[2].position.x
        y = data.pose[2].position.y
        z = data.pose[2].position.z
        self.obstacle_pose = [x,y,z]    #障害物の姿勢を代入

    def start_subscriber(self):     #購読をスタート
        rospy.Subscriber("/gazebo/model_states", ModelStates, self.callback)    
        # /gazebo/model_states から　gazebo_msgs/ModelStates 型のトピックを購読　トピックが更新されるたびに　self.callback を呼ぶ

    def target(self):
        rate = rospy.Rate(1)    #Rateクラスのインスタンス   rateを１で
        rospy.sleep(1)          #1秒スリープ
        while not rospy.is_shutdown():      #シャットダウンフラグが立っていなければ、
            self.planning_scene.removeCollisionObject("demo_cube")  #オブジェクトの削除
            self.planning_scene.removeCollisionObject("obstacle")   #オブジェクトの削除
            self.planning_scene.addCube("demo_cube", 0.06,self.model_pose[0],self.model_pose[1],self.model_pose[2])         #一辺が0.06の正方形をmodel_pose(座標)に追加
            self.planning_scene.addBox("obstacle", 0.540614, 0.083603, 0.54373, self.obstacle_pose[0],self.obstacle_pose[1],self.obstacle_pose[2])#---の大きさの箱をobstacle_pose(座標)に追加

            print self.model_pose       #model_poseを表示
            group = moveit_commander.MoveGroupCommander("manipulator")      #MoveGroupCommander クラスのインスタンス
            #print group.get_current_pose().pose
            pose_target = geometry_msgs.msg.Pose()
            pose = group.get_current_pose().pose       #エンドエフェクタの位置姿勢
            pose_target = geometry_msgs.msg.Pose()  #geometry_msgs.pose のインスタンス　これに入れるとトピックに反映される？
            pose_target.orientation.x = pose.orientation.x  #
            pose_target.orientation.y = pose.orientation.y  #
            pose_target.orientation.z = pose.orientation.z  #
            pose_target.orientation.w = pose.orientation.w  #トピックに　四元数を代入
            #pose_target.position.x = pose.position.x
            #pose_target.position.y = pose.position.y
            #pose_target.position.z = pose.position.z
            pose_target.position.x = self.model_pose[0]         #
            pose_target.position.y = self.model_pose[1]         #
            pose_target.position.z = self.model_pose[2]+0.05    #トピックに　座標を代入

            group.set_pose_target(pose_target)      #ターゲットをセット
            group.go()      #移動

            rospy.sleep(1)  #1秒スリープ



if __name__ == '__main__':
    try:
        r = Reaching()          #Reachingクラスのインスタンス
        r.start_subscriber()    #購読を開始
        r.target()              #動く
        
    except rospy.ROSInterruptException:
        pass

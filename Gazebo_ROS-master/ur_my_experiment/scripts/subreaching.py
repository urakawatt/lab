#!/usr/bin/env python
# -*- coding: utf-8 -*-
# license removed for brevity

#   20190725    Urakawa
#   指定したトピックを購読させて、トピック越しに操作する　購読者側


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

from std_msgs.msg import Bool
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Vector3
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped

from sensor_msgs.msg import (   PointCloud2,
                                PointField)
import sensor_msgs.point_cloud2 as pc2

import tf


 

class Reaching:
    def __init__(self):
        rospy.init_node('reaching', anonymous=True)#ノードの初期化　reaching ていう名前
        self.robot = moveit_commander.RobotCommander()# インスタンスの作成
        self.model_pose = [0.0,0.0,0.0]     #モデルの姿勢
        self.obstacle_pose = [0.0,0.0,0.0]  #障害物の位置
        self.subsc_pose=[0.0,0.0,0.0]       #購読した座標
        self.subsc_orientation=[0.0,0.0,0.0,1.0]#購読した四元数
        self.set_forbidden()    #禁止エリアの初期化
        self.set_init_pose()    #位置姿勢の初期化
        self.before_pose=[0,0,0] #前回の場所
        self.pcarray=0                  #pointcloud を np array にしたものを入れる
        self.executeFlag=False          #unity コントローラ B ボタンと対応
        self.before_executeFlag=False   #前フレームの executeFlag
        self.waypoints=[]
        self.way_flag=False             #unity コントローラの 中指のボタンに対応
        self.before_wayflag=False       #前フレームのway_flag
        self.infirst_frame=True         #最初のフレーム
        self.calc_way_flag=False


    def set_ZEDbase(self):
        listener = tf.TransformListener()

        listener.waitForTransform('world','ee_link',rospy.Time(0),rospy.Duration(2.0))
        (self.trans,rot)=listener.lookupTransform('/world','/ee_link',rospy.Time(0)) # trans(x,y,z) rot (x,y,z,w)

        print('trans = '+str(self.trans))
        br = tf.TransformBroadcaster()
        br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),(0.0,0.0,0.0,1.0),rospy.Time.now(),'base_forZED','world')
            
        
    def set_forbidden(self):
        #set forbidden erea
        self.planning_scene = PlanningSceneInterface("base_link")   #PlanningSceneInterface のインスタンスの作成

        self.planning_scene.removeCollisionObject("my_ground")
        self.planning_scene.addCube("my_ground", 2, 0, 0, -1.0)
        self.planning_scene.addBox("obstacle", 0.1, 0.5, 1, -0.3,0,0.5)
        self.planning_scene.addBox("obstacle2", 0.5, 0.1, 1, 0,-0.3,0.5)
        self.planning_scene.addCube("demo_cube", 0.06,0,0.3,0)

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
        pose = [-1.26 , -0.64 , -2.44 , -0.66 , 1.56 , 0.007]
        move_group.moveToJointPosition(joint_names, pose, wait=False)#joint_names を pose に動かす
        move_group.get_move_action().wait_for_result()      #wait result
        result = move_group.get_move_action().get_result()  #result を代入
        move_group.get_move_action().cancel_all_goals()     #すべてのゴールをキャンセル

        self.state={'default':0,'hold':1,'way_standby':2,'plan_standby':3}
         # default       : 何もしていない　target のセットか hold button を待つ
         # hold          : waypoint のセットを受け付ける hold button が離れたら終了
         #way_standby    : execute button が押されるのを待つ 押されたら default へ  waypoint の設置をした場合
         #plan_standby   : execute button が押されるのを待つ 押されたら default へ  waypoint を使わなかった場合
        self.now_state=self.state['default']    #現在フレームの状態

        self.set_ZEDbase()


    def callback(self,data):    #トピックにデータが追加されるたびに呼ばれる
        x = data.pose[1].position.x
        y = data.pose[1].position.y
        z = data.pose[1].position.z
        self.model_pose = [x,y,z]       #modelの姿勢を代入
        
        x = data.pose[2].position.x
        y = data.pose[2].position.y
        z = data.pose[2].position.z
        self.obstacle_pose = [x,y,z]    #障害物の姿勢を代入

    def callbacksub(self,data):
        x=data.x
        y=data.y
        z=data.z
        self.subsc_pose=[x,y,z]         #購読した座標を代入

    def callbackunity(self,data):
        x=data.pose.position.x
        y=data.pose.position.y
        z=data.pose.position.z
        self.subsc_pose=[y,-x,z]             #unity からの座標 座標変換も行っている

        x=data.pose.orientation.x
        y=data.pose.orientation.y
        z=data.pose.orientation.z
        w=data.pose.orientation.w
        self.subsc_orientation=[y,-x,z,w]    #unity からの四元数
        
    def rtabcallback(self,data):
        # dtype_list = [(f.name, np.float32) for f in data.fields]
        # cloud_arr = np.fromstring(data.data, dtype_list)
        # self.pcarray = np.reshape(cloud_arr, (data.height, data.width)) 
        # print(self.pcarray)
        print('rtab subscribed ')

    def excallback(self,data):
        self.executeFlag=data.data
        #print(data.data)

    def waycallback(self,data):
        self.way_flag = data.data

        self.wayflagcalc()

    def wayflagcalc(self):
        if self.before_wayflag != self.way_flag:
            if self.calc_way_flag:
                self.calc_way_flag=False
            else:
                self.calc_way_flag=True
        self.before_wayflag = self.way_flag


    def start_subscriber(self):     #購読をスタート
        rospy.Subscriber("/gazebo/model_states", ModelStates, self.callback)    
        # /gazebo/model_states から　gazebo_msgs/ModelStates 型のトピックを購読　トピックが更新されるたびに　self.callback を呼ぶ
        #rospy.Subscriber("/UR/reaching/pose",Vector3,self.callbacksub)
        rospy.Subscriber("/unity/target",PoseStamped,self.callbackunity)#unityから配信しているトピックを購読
        #rospy.Subscriber('/rtabmap/cloud_map', PointCloud2, self.rtabcallback) #zed で slam したpointcloud を購読
        rospy.Subscriber('/unity/execute',Bool,self.excallback)
        rospy.Subscriber('/unity/wayflag',Bool,self.waycallback)

    def change_state(self,target):
         #self.state = {'default':0,'hold':1,'way_standby':2,'plan_standby':3}
         # default       : 何もしていない　target のセットか hold button を待つ
         # hold          : waypoint のセットを受け付ける hold button が離れたら終了
         #way_standby    : execute button が押されるのを待つ 押されたら default へ  waypoint の設置をした場合  target が指定されたら plan_standby に以降
         #plan_standby   : execute button が押されるのを待つ 押されたら default へ  waypoint を使わなかった場合

        set_flag = (self.before_pose != target.position)  # target の位置が変化している = トリガーが押された
        #self.calc_way_flag                               # hold button が押されている
        exe_flag = (self.before_executeFlag != self.executeFlag)# executeFlag が前フレームと違う = execute button が押された
        print('set    '+str(set_flag))
        print('hold   '+str(self.calc_way_flag))
        print('exe    '+str(exe_flag))
        print('state   '+str(self.now_state))

        if self.now_state == self.state['default']:
            if set_flag:
                self.now_state = self.state['plan_standby']
            elif self.calc_way_flag:
                self.now_state = self.state['hold']
        
        elif self.now_state == self.state['hold']:
            if not self.calc_way_flag:
                self.now_state = self.state['way_standby']
        
        elif self.now_state == self.state['way_standby']:
            if set_flag:
                self.now_state = self.state['plan_standby']
            elif exe_flag:
                self.now_state = self.state['default']
        
        elif self.now_state == self.state['plan_standby']:
            if exe_flag:
                self.now_state = self.state['default']
            elif self.calc_way_flag:
                self.now_state = self.state['hold']
        



        


    def target(self):
        rate = rospy.Rate(1)    #Rateクラスのインスタンス   rateを１で
        rospy.sleep(1)          #1秒スリープ
        useway=False

        while not rospy.is_shutdown():      #シャットダウンフラグが立っていなければ、

            print self.model_pose       #model_poseを表示
            group = moveit_commander.MoveGroupCommander("manipulator")      #MoveGroupCommander クラスのインスタンス
            #print group.get_current_pose().pose
            pose_target = geometry_msgs.msg.Pose()
            pose = group.get_current_pose().pose       #エンドエフェクタの位置姿勢
            pose_target = geometry_msgs.msg.Pose()  #geometry_msgs.pose のインスタンス　ここにターゲット設定
            pose_target.orientation.x = self.subsc_orientation[0]
            pose_target.orientation.y = self.subsc_orientation[1]
            pose_target.orientation.z = self.subsc_orientation[2]
            pose_target.orientation.w = self.subsc_orientation[3]#トピックから　四元数を代入


            pose_target.position.x = self.subsc_pose[0]         #
            pose_target.position.y = self.subsc_pose[1]       #
            pose_target.position.z = self.subsc_pose[2]   #トピックから　座標を代入

            br = tf.TransformBroadcaster()
            br.sendTransform((self.trans[0],self.trans[1],self.trans[2]),(0.0,0.0,0.8509035,0.525322),rospy.Time.now(),'base_forZED','world')
            #逐一ブロードキャストする

            

            if self.infirst_frame:
                self.before_pose=pose_target.position
                self.infirst_frame=False

            #self.planning_scene.removeCollisionObject("targetOBJ")
            #self.planning_scene.addCube("targetOBJ", 0.005,self.subsc_pose[0] ,self.subsc_pose[1] ,self.subsc_pose[2] )

            self.way_flag=False

         #self.state={'default':0,'hold':1,'way_standby':2,'plan_standby':3}
         # default       : 何もしていない　target のセットか hold button を待つ
         # hold          : waypoint のセットを受け付ける hold button が離れたら終了
         #way_standby    : execute button が押されるのを待つ 押されたら default へ  waypoint の設置をした場合
         #plan_standby   : execute button が押されるのを待つ 押されたら default へ  waypoint を使わなかった場合

            exe_flag = (self.before_executeFlag != self.executeFlag)# executeFlag が前フレームと違う = execute button が押された
            if self.now_state == self.state['default']:
                if self.before_pose!=pose_target.position:
                    group.set_pose_target(pose_target)
                    print ('    Set Target !!!\n')
                    print(pose_target)
                    
            
            if self.now_state == self.state['hold']:
                if self.before_pose!=pose_target.position:
                    self.waypoints.append(copy.deepcopy(pose_target))
                    print('     Append Target !!!')

            if self.now_state == self.state['way_standby']:
                plan , fraction =group.compute_cartesian_path(self.waypoints,0.01,0.0)

                if self.before_pose!=pose_target.position:
                    group.set_pose_target(pose_target)
                    print ('    Set Target !!!\n')
                    print(pose_target)

                elif exe_flag:
                    group.execute(plan)
                    print(' Planning Execute !!!')
                    print(self.waypoints)
                    self.waypoints=[]
            
            if self.now_state == self.state['plan_standby']:
                group.set_pose_target(pose_target)
                group.plan()

                if self.before_pose!=pose_target.position:
                    group.set_pose_target(pose_target)
                    print ('    Set Target !!!\n')
                    print(pose_target)

                elif exe_flag:
                    group.go()
                    print(' Planning Go !!!')
            self.change_state(pose_target)
            

            

            self.before_executeFlag=self.executeFlag
            self.before_pose=pose_target.position
           
            rospy.sleep(2)  #1秒スリープ



if __name__ == '__main__':
    try:
        r = Reaching()          #Reachingクラスのインスタンス
        r.start_subscriber()    #購読を開始
        r.target()              #動く
        
    except rospy.ROSInterruptException:
        pass

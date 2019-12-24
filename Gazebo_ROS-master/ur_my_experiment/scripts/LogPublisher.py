#!/usr/bin/env python
# -*- coding: utf-8 -*-


#   20191115   Urakawa
#　 /rosout ー＞ros 関連のログを吐き出してる
#   /rosout の msg の部分を読み取って
#   ABORTED: No motion plan found. No execution attempted.
#   が出ているのを確認したら unity/ROS# が受け取れる形でpublish する

#    Execution request received
#    が出ているのを確認したら　publish する
import rospy
from std_msgs.msg import Bool
from rosgraph_msgs.msg import Log
import time
from geometry_msgs.msg import PoseStamped

sec=0
errmsg = 'ABORTED: No motion plan found. No execution attempted.'
errmsg2 = 'Solution found but controller failed during execution'
exmsg='Execution request received'

def callback(data):
    starttime=time.time()
    
    #extalker((exmsg in data.msg))
    talker((errmsg in data.msg) or (errmsg2 in data.msg))
    print(time.time()-starttime)
    
def listener():
    rospy.init_node('LogPublisher',anonymous=True)
    rospy.Subscriber("/rosout", Log, callback)
    rospy.spin()


def talker(result=False):
    pub = rospy.Publisher('/unity/reachingerror', Bool, queue_size=10)
    pose=Bool()
    pose.data=result

    pub.publish(pose)

#def extalker(result=False):
 #   pub = rospy.Publisher('/unity/executed_fromRos',Bool,queue_size=10)
  #  f=Bool()
   # f.data=result
    #pub.publish(f)



if __name__ == '__main__':
    listener()

    
    

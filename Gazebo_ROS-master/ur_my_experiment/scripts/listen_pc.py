#!/usr/bin/env python
# -*- coding: utf-8 -*-

#pcl_linstener .cpp でダウンサンプルした点群の　座標とかを取ってきて処理とかして subreaching .py に渡す

import rospy
from sensor_msgs.msg import PointCloud2
import sensor_msgs.point_cloud2 as pc2
import tf
import geometry_msgs.msg
import time




class SubscribePointCloud():
    def __init__(self):
        #print('aaaaa')
        

        self.Points=0
        rospy.init_node('subscribe_custom_point_cloud')
        self.listener = tf.TransformListener()
        #self.t = self.listener.getLatestCommonTime('/base_link','/base_forZED')

        rospy.Subscriber('/pcl/downsampling', PointCloud2, self.callback)
        
        

    def callback(self, point_cloud):
        starttime=time.time()
    
        self.Points=[ data[0:3] for data in pc2.read_points(point_cloud)]
        self.Points=[self.from_base(data) for data in self.Points]
        self.Points=[data for data in self.Points if self.Size(data)<0.5**2]
        
        print('Points  =  '+ str(len(self.Points)))
        print('It took '+str(time.time()-starttime)+' sec')
    

    def getpoints(self):
        return self.Points

    def from_base(self,data):
        # tf を使って data に与えられる座標データを base_link 座標系に変換
        coo = geometry_msgs.msg.PoseStamped()
        coo.header.frame_id = 'zed_camera_center'
        coo.pose.orientation.w=1.0
        coo.pose.position.x=data[0]
        coo.pose.position.y=data[1]
        coo.pose.position.z=data[2]
        result = self.listener.transformPose('/base_link',coo)
        return [result.pose.position.x ,result.pose.position.y ,result.pose.position.z]

    def Size(self,data):
        return data[0]**2 + data[1]**2 + data[2]**2

def main():
    try:
        sub=SubscribePointCloud()
        print(sub.getpoints())
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

def GetPoints():
    # 点群の座標リストを渡す
    sub=SubscribePointCloud()
    rospy.sleep(1)
    #もし subscribe できていなければ0が返る
    return sub.getpoints()

if __name__ == '__main__':
    main()
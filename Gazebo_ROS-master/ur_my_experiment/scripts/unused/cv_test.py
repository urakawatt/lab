#!/usr/bin/env python
# license removed for brevity
import rospy
import cv2
from std_msgs.msg import String
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import random,math
import numpy as np
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray



class Image_Converter:
    def __init__(self):
        self.image_pub = rospy.Publisher("image_topic_2",Image)
        self.bridge = CvBridge()
        
        #HughCircle using RGB image
        self.image_sub = rospy.Subscriber("/depth_camera_rgb/image_raw",Image,self.callback1)
        #HughCircle using depth image
        self.image_sub = rospy.Subscriber("/depth_camera/depth_registered/image_raw",Image,self.callback2)

        self.coordinate = [0.0,0.0]

        self.marker_pub = rospy.Publisher("visualization_marker_array", MarkerArray)

    def callback1(self,data):

        position = [0.0,0.0]

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
        
        #(rows,cols,channels) = cv_image.shape
        #if cols > 60 and rows > 60 :
        #    cv2.circle(cv_image, (50,50), 10, 255)

        #Hough Circle Detection Testing
        #imgsize = cv_image.shape
        #simg_width=imgsize[1]
        #simg_height=imgsize[0]
        #cv_image=cv2.resize(cv_image,(simg_width/2,simg_height/2))
        cimage = cv2.cvtColor(cv_image,cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(cimage,cv2.cv.CV_HOUGH_GRADIENT,1,20, param1=50,param2=20,minRadius=0,maxRadius=100)
        if circles != None:
            a,b,c = circles.shape
            print "num of circles: ",b
            for i in range(b):
                cv2.circle(cv_image, (circles[0][i][0], circles[0][i][1]), circles[0][i][2], (0, 0, 255), 1)
                #cv2.circle(cv_image, (circles[0][i][0], circles[0][i][1]), 2, (0, 255, 0), 1)
            position[0] = circles[0][0][0]
            position[1] = circles[0][0][1]
            self.coordinate = [position[0],position[1]]
        else:
            print "none"

        cv2.imshow("Image window", cv_image)
        cv2.waitKey(3)
        
        #try:
        #    self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
        #except CvBridgeError as e:
        #    print(e)

    def callback2(self,data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "passthrough")
        except CvBridgeError as e:
            print(e)

        depth_array = np.array(cv_image, dtype=np.float32)
        #print np.max(depth_array)

        print self.coordinate
        x = int(self.coordinate[0])
        y = int(self.coordinate[1])
        print x,y
        print depth_array[y][x]

        Z = depth_array[y][x]
        X = Z*(x-320)/554
        Y = Z*(y-240)/554
        print X,Y,Z
        
        markerArray = MarkerArray()
        marker = Marker()
        marker.header.frame_id = "/depth_camera_frame"
        marker.type = marker.SPHERE
        marker.action = marker.ADD
        marker.scale.x = 0.02
        marker.scale.y = 0.02
        marker.scale.z = 0.02
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        marker.pose.orientation.w = 1.0
        marker.pose.position.x = X
        marker.pose.position.y = Y
        marker.pose.position.z = Z

        markerArray.markers.append(marker)
        self.marker_pub.publish(markerArray)


def main():
    ic = Image_Converter()
    rospy.init_node('image_converter', anonymous=True)
    
    rate = rospy.Rate(1) # 10hz
    while not rospy.is_shutdown():
        v = rospy.get_time()
        rospy.loginfo(v)
        
        rate.sleep()

    cv2.destroyAllWindows()



if __name__ == '__main__':
    main()
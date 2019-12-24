//20191223 urakawa

/*
pointcloud2 のトピック subscribe して　ダウンサンプリングして　別のトピックへ publish
*/
#include <ros/ros.h>
#include <iostream>
#include <math.h> 
#include <time.h>
#include <pcl/io/vtk_io.h>
#include <pcl/ModelCoefficients.h> 
#include <pcl/io/openni_grabber.h> 
#include <pcl/io/pcd_io.h> 
#include <pcl/point_types.h> 
#include <pcl/sample_consensus/method_types.h> 
#include <pcl/sample_consensus/model_types.h> 
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/segmentation/sac_segmentation.h> 
#include <pcl/surface/gp3.h>
#include <pcl/visualization/pcl_visualizer.h>
#include <pcl/visualization/cloud_viewer.h> 
#include <pcl/filters/passthrough.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/features/normal_3d.h>
#include <pcl/console/parse.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl_ros/io/pcd_io.h>
#include <sensor_msgs/image_encodings.h>
#include <geometry_msgs/Point.h>
#include <geometry_msgs/Twist.h>
#include <pcl_ros/point_cloud.h>

class DownSampling{
    private:
    ros::NodeHandle node; //ノードハンドラの宣言
    ros::Subscriber sub;  //Subdcriberの宣言
 //点群の位置情報+色情報RGBの宣言->point cloudの処理で何を使うか
    ros::Publisher pub; //Publisherの宣言



    public:
        DownSampling()
        {//コンストラクタ
            sub = node.subscribe ("/rtabmap/cloud_map", 1,  &DownSampling::callback,this);
            // /rtabmap/cloud_map をサブスクライブ　リアルタイム性がほしいので第二引数は１


        }
    
/************************************************************************
ダウンサンプリング
size[m]単位ででダウンサンプリングを行う
*************************************************************************/
///

void downsample(pcl::PCLPointCloud2::Ptr& cloud,pcl::PCLPointCloud2::Ptr& out_cloud, float size)
{
    pcl::VoxelGrid<pcl::PCLPointCloud2> sor;
    sor.setInputCloud (cloud);
    //sor.setLeafSize (0.003f, 0.003f, 0.003f);　//<-サイズ指定してあげる必要?
    sor.setLeafSize (size, size, size);
    sor.setDownsampleAllData(true);
    sor.filter (*out_cloud);
}

/************************************************
callback 関数
 * **********************************************/
void callback( const sensor_msgs::PointCloud2ConstPtr& cloud ){ //constが付いている値はあとから変更不可、::はsensor_msgの名前空間の中にPointCloud2ConstPtrが属しているという意味

    pcl::PCLPointCloud2 pcl_pc2 ,down_cloud; //pcl_pc2 : もらった点群　　　　down_cloud : downsample したあとのやつをいれるとこ
    pcl_conversions::toPCL(*cloud,pcl_pc2);
    pcl::PointCloud<pcl::PointXYZ>::Ptr temp_cloud(new pcl::PointCloud<pcl::PointXYZ>);
    pcl::fromPCLPointCloud2(pcl_pc2,*temp_cloud);
    //ここまで sensor_msgs pointcloud2constptr から pcl pclpointcloud2 への変換

    pcl::PCLPointCloud2::Ptr in_cloud(new pcl::PCLPointCloud2());
    pcl::PCLPointCloud2::Ptr down(new pcl::PCLPointCloud2());

    // Ptr のやつに変換
    *in_cloud = pcl_pc2;
    *down = down_cloud;

    DownSampling::downsample(in_cloud,down,0.25);

    // ROS の型に変換
    sensor_msgs::PointCloud2 point;
    pcl_conversions::fromPCL(*down,point);

     pub = node.advertise<sensor_msgs::PointCloud2>("/pcl/downsampling",100);//publisher の定義

    pub.publish(point);// publish

    std::cout << "Subscribe OK!!\n" <<endl;
  }

};

int main(int argc, char **argv)
{

    ros::init(argc, argv, "pcl_listener");
    //subsc する　ー＞　ダウンサンプル　ー＞　publish
    DownSampling sample;

    ros::spin();


    return 0;
}

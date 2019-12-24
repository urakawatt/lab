
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
    pcl::PointCloud<pcl::PointXYZRGB> in_cloud; //点群の位置情報+色情報RGBの宣言->point cloudの処理で何を使うか
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

void downsample(pcl::PointCloud<pcl::PointXYZRGB>::Ptr& cloud,pcl::PointCloud<pcl::PointXYZRGB>::Ptr& out_cloud, float size)
{
    pcl::VoxelGrid<pcl::PointXYZRGB> sor;
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
    if ((cloud->width * cloud->height) == 0)
      return;
    pcl::fromROSMsg (*cloud, in_cloud);

    if ((in_cloud.width * in_cloud.height) == 0)
      return;

    pcl::PCLPointCloud2 pcl_pc2 , pcl_forPub;
    pcl_conversions::toPCL(*cloud,pcl_pc2);
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr input_cloud(new pcl::PointCloud<pcl::PointXYZRGB>);
    pcl::fromPCLPointCloud2(pcl_pc2,*input_cloud);
    
    
    pcl::PointCloud<pcl::PointXYZRGB>::Ptr down_cloud (new pcl::PointCloud<pcl::PointXYZRGB>);
    DownSampling::downsample(input_cloud,down_cloud,0.25);
    std::cout << typeid(input_cloud).name() <<endl;
    std::cout << typeid(down_cloud).name() <<endl;

    std::cerr << "PointCloud before filtering: " << input_cloud->width * input_cloud->height 
       << " data points (" << pcl::getFieldsList (*input_cloud) << ").\n";

    std::cerr << "PointCloud after filtering: " << down_cloud->width * down_cloud->height 
       << " data points (" << pcl::getFieldsList (*down_cloud) << ").\n";

     pub = node.advertise<sensor_msgs::PointCloud2>("/pcl/downsampling",100);//publisher の定義


    sensor_msgs::PointCloud2 point;
    pcl::toROSMsg( *down_cloud, point);
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

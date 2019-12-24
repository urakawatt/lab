日本語でメモ

Fetch Robotを動かす実験を行うのにfetch_my_experimentというパッケージを独立して作る。  
以下は ROS indigo + gazebo7 の環境で行っている。  


#####ROS indigo で gazebo7 を使う環境を整える  
http://gazebosim.org/tutorials?tut=ros_wrapper_versions　ここと  
http://gazebosim.org/tutorials?tut=install_ubuntu&cat=install ここと  
http://thetechdeskblog.blogspot.jp/2016/07/installing-ros-indigo-with-gazebo-7-or.html　ここを参考に  

$ sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'  
$ wget http://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -  
$ sudo apt-get update  
これでosrfのレポジトリを追加して  
$ sudo apt-get remove gazebo2　　gazebo2を消して  
$ sudo apt-get install ros-indigo-gazebo7-ros-pkgs ros-indigo-gazebo7-ros-control  
これでgazebo7をインストールした  
そしてpluginのコントロールとかにつかうrosパッケージを以下でインストール  
$ sudo apt-get install ros-indigo-ros-control ros-indigo-ros-controllers  


#####Fetch Robot　のシミュレーションを使えるようにする。  
以下は私の環境で試して実現できたやりかたであるので、参考までに。  
上のようにしてgazebo7に差し替えると
$ apt-cache search ros-indigo-fetch*　　これではインストールできなかったので。  
以下の  
fetch_arm_control  
fetch_auto_dock_msgs  
fetch_bringup  
fetch_calibration  
fetch_depth_layer  
fetch_description  
fetch_driver_msgs  
fetch_ikfast_plugin  
fetch_maps  
fetch_moveit_config  
fetch_navigation  
fetch_pbd_interaction  
fetch_social_gaze  
fetch_teleop  
fetch_tools  
fetchに関するパッケージのリストをapt-getでそれぞれ個別にインストール  
次に  
https://github.com/fetchrobotics/fetch_gazebo  
https://github.com/fetchrobotics/robot_controllers  
この２つ　fetch_gazebo と robot_controllers のパッケージをワークディレクトリにコピーしてcatkin_makeでビルド  
そして以下をapt-getでインストール  
$ sudo apt-get install ros-indigo-rgbd-launch  
$ sudo apt-get install ros-indigo-simple-grasping  
これで環境は整って  
$ roslaunch fetch_gazebo simulation.launch  
$ roslaunch fetch_moveit_config move_group.launch  
$ rviz rviz  
この３つを立ち上げると、rviz上でmoveitをguiでの操作がgazeboでちゃんと実行された。  


#####Fetchをmoveitで動かすテスト  
カメラとアームを初期位置までもってゆくスクリプト  

$ roslaunch fetch_my_experiment fetch.launch  
$ rosrun fetch_my_experiment moveit_test.py  

こんな感じ  
!(https://github.com/smomoi/Gazebo_ROS/blob/master/fetch_my_experiment/screenshots/image4.png)


#####対象物の座標を既知として与え、そこにリーチするスクリプト  
以下でgazebo上にfetchを登場させ

$ roslaunch fetch_my_experiment fetch.launch  

以下のスクリプトの実行で土台を目的地まで移動させ、さらに既知のデータとして受け取った対処物の座標をtfとして発行して座標変換を
容易に行えるようにする。  

$ rosrun fetch_my_experiment move_base.py  

リーチするスクリプト  
以下で土台移動スクリプトが発行する対象物のtfをもとにFetchのアームで対象物まで真上からリーチングする  

$ rosrun fetch_my_experiment reaching.py  

スクリーンショットはこんな感じ  
!(https://github.com/smomoi/Gazebo_ROS/blob/master/fetch_my_experiment/screenshots/image6.png)
!(https://github.com/smomoi/Gazebo_ROS/blob/master/fetch_my_experiment/screenshots/image9.png)
青いボックスの対象物を移動させても、fetchのアームの先端がそこに合わせてついてくる。


#####対象物をORKで認識する  
ORK Object Recognition Kitchen　パッケージを導入することによる簡単に、深度カメラからの３次元情報とデータベースに
登録しておいた対象物の３次元情報を照合して対象物を認識しその座標を取得する。  
$ sudo apt-get install ros-indigo-object-recognition-*　　　でインストール  
物体の登録と認識は公式チュートリアルの通りにやればすんなりできた。  
そしてFetch Robot用ののORKのconfigが必要で、とくにFetchが発行するトピックを  
parameters:  
    rgb_frame_id: '/head_camera_depth_optical_frame'  
    rgb_image_topic: '/head_camera/rgb/image_raw'  
    rgb_camera_info: '/head_camera/rgb/camera_info'  
    depth_image_topic: '/head_camera/depth_registered/image_raw'  
    depth_camera_info: '/head_camera/depth_registered/camera_info'  
このようにして正確に書き換える必要がある。これはconfigディレクトリ内にあるファイルの一部である。  
これさえできればORKの起動も簡単でチュートリアルの通りにやればすんなり実行できた。  
ちなみにこのconfigファイルの設定についてのドキュメントが見当たらず苦労したが、ORKを使った他のロボットの例がレポジトリとして少ないが見つけられてそれを参考にした。ちょっとなんのレポジトリだったかは忘れてしまった。多分検索すれば出てくる。    

$ roslaunch fetch_my_experiment fetch_ork.launch  
これでorkのノードも一緒に起動する  

$ rosrun fetch_my_experiment set_position.py  
これでカメラヘッドの角度を調節する  

gazebo上にはデータモデルとして登録したcoke canと同じメッシュファイルのオブジェクトを配置してあるので、  
ORKのデータベースと照合してこれをcoke canとして認識している様子がわかる。  
!(https://github.com/smomoi/Gazebo_ROS/blob/master/fetch_my_experiment/screenshots/image13.png)

リーチング動作についてはFetchが私の環境では重くてめんどくさいので割愛することにする。  

日本語でメモ

ur_my_experimentというパッケージをuniversal_robotのROSパッケージ  
https://github.com/ros-industrial/universal_robot　とは別に作って、制御スクリプトなどを  
動かす実験を行う独立したパッケージを作る。

URは  
git clone https://github.com/ros-industrial/universal_robot.git  
でパッケージをクローンしてcatkin_makeすれば普通に使えるようになる。  
こうして導入したURパッケージのあるROSのワークディレクトリと同じ場所にこのur_my_experimentをコピーすれば使えるようになる。  
以下の実行環境は ROS indigo + gazebo7　である。

$ roslaunch ur_my_experiment ur10_moveit.launch  
を実行すれば gazebo と rviz が同時に立ち上がり  
moveitのplanningをguiで操作して実行すればgazeboでも指示通りにURが動く。  


#####URをmoveitで動かす三種類のやりかたテスト  
moveit_test.py スクリプト内に
ターゲット座標を与えてるやり方  
ジョイント座標を与えるやり方  
Cartesian座標に沿って移動するやり方。  
の３種類のやり方でmoveitでURを動かす例が書いてある。


#####対象物の座標を既知として与え、そこにリーチするスクリプト  
sim.world　がこのスクリプトを動かすためのplaygroundになっている。  
リーチする対象物と障害物の２つがworldに配置されている。  
この２つ物体をアームが届く範囲で位置を変えると、アームの先端が障害物を避け対象物の真上にリーチするようになっている。  
$ roslaunch ur_my_experiment ur10_moveit.launch 　これでgazeboとrvizを起動し  
$ rosrun ur_my_experiment reaching.py　　　これでリーチ動作のスクリプトを起動する  
こんな感じ
!(https://github.com/smomoi/Gazebo_ROS/blob/master/ur_my_experiment/screenshots/image2.png)


#####対象物の座標をCVの画像処理+Depth Cameraの深度座標で得る  
Depth CameraつきのURのplaygroundが sim_for_camera.world　である。  
ur_and_camera.urdf.xacro　が ur本体のxacroと depth_camera.urdf.xacro　をインクルードして一つのモデルとして  
gazebo及びrviz上にスポーンされている。  
真上に付けられたdepth cameraが球体を二次元画像処理として認識しその中心座標に当たる部分までの深度を計算して、  
球体のてっぺんにマカーで印をつけている。  
そしてこのマカーの座標へURがリーチする。  

深度画像の任意のピクセルに対応するリアル・ワールドの３次元座標は以下のように求められる。  
Z = depth_array[y][x]  
X = Z*(x-320)/554  
Y = Z*(y-240)/554   
この透視投影変換におけるパラメータはrostopicコマンド  
$ rostopic echo /camera_info  
を実行することで情報が得られ、この中のP行列の値から知った。  
http://docs.ros.org/api/sensor_msgs/html/msg/CameraInfo.html　　このROSのデータ型リファレンスに各パラメータの説明が
ある。  
この変換式によってカメラキャリブレーションを行うことができる。  

$ roslaunch ur_my_experiment ur10_and_camera.launch　　　これでgazeboとrvizを起動し  
$ rosrun ur_my_experiment cv_test.py　　　これで画像処理ノードを起動し  
$ rosrun ur_my_experiment percept_reaching.py　　　そしてこれでURのリーチ動作のノードを起動する  
depth cameraで対象物を認識しその座標までURの先端が移動するだけの動作を実現する。  
これは先ほどのreaching.pyとほぼ同じコードだが、対象物が既知のデータではなく画像処理からのデータを受けっとって処理する
点が異なる。  
カメラでとらえた対象物の座標をURのbase_linkeからの座標に変換するのにわざわざtfを発行しなくてもいいとは思うが
手っ取り早く動かしたかったのでこのようにした。  
もろもろ動作が限定的で安定しないが、depth cameraから認識した対象物の３次元座標を取得し、そこにエンドエフェクターを
リーチさせる動作のあらましはこれでざっくり理解できるだろう。  
また画像処理の部分とその結果のデータを受け取りリーチングを行う部分を別々のノードとして記述できるところもいい。  
スクリーンショットはこんな感じ  
!(https://github.com/smomoi/Gazebo_ROS/blob/master/ur_my_experiment/screenshots/image17.png)
!(https://github.com/smomoi/Gazebo_ROS/blob/master/ur_my_experiment/screenshots/image16.png)


#####Depth Camera単独でテスト  
このテストでは depth_camera.urdf をスポーンして水平に向けたdepth cameraに対して球体を写している。  
これで画像処理の部分だけを単体でテストしてみる。    
球体を depth camera に近づけたり話したり、視野の端にやったりしてもちゃんと球体のてっぺんにマーカーがつくのがわかる。  

$ roslaunch ur_my_experiment only_camera.launch　　　これでgazeboとrvizを起動し  
$ rosrun ur_my_experiment cv_test.py　　　　これでカメラの処理を起動させる  

こんな感じになる。
!(https://github.com/smomoi/Gazebo_ROS/blob/master/ur_my_experiment/screenshots/image10.png)

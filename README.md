# Iot_4764_Final_project
The City-Bin, a work that integrates technology and practicality, was designed for garbage sorting and new smart city services. It can be deployed both in home or public areas such as city streets, served as a defender of environment. City-Bin uses yolov5  Computer Vision Algorithm to process the image containing metal, paper, plastic trash collected by USB camera, and then rotate the  lid with drop hole depending on the trash type returned by cloud server. Not only this, City-Bin could gather information about  itself and upload it to the cloud, then display the percentage remaining capacity in each City-Bin on a visualized online map application. Here is the group photo of our team, and more information about our project，please check it out in next session of the project web page.
Web page link: 
![pic13](https://user-images.githubusercontent.com/90977332/146276667-684c99c6-0ffc-4127-a9bb-d0ac3e339286.jpg)
Our team member including YisenJia, ChongzhiXu, HanshanLi work for more than 2 weeks to finish this project! Here we wanna express our gratitude to Professor Fred Jiang and teaching assistant Scott Zhao and Kevin Hou. Without their help, we can't finish this project with such good results.
# File explanation:
1. main.py
main.py contains all the functions for trash dropping iteration, including lid rotation, volume detection, raspberry pi display, driver and motor control.
2. final_project_classes
final_project_classes contains all the class of different sensor and conponents. Including detect display, rotate display, different trash display, camera, API and motor.
3. server.py
server.py is used to run a server and interact with RPi 4, including fuctions of image prediction, volume recording, locating and resetting the volume distribution.
4. yolo_play.py
yolo_play.py is used to train models and get prediction of images.

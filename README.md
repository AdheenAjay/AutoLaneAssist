# AutoLaneAssist
>Autonomous cars are going to rule the roads. Why don't we try building a prototype of it.

Autonomous cars are expected to drive from a point to another all by itself. The conventional technologies for self-driving cards are designed to detect roads/lanes and obstacles on it. They use many sensors viz - camera, GPS, IMS etc. From the lane information, another sub module has to calculate the best steering angle and it has to plan its path ahead. Trust me, it is a pretty complicated design.

Researchers in Nvidia developed an end-to-end deep learning system for self-driving cars. Their system reads camera images and outputs steering angle, there by they call it an end-to-end system. They designed a deep CNN network to understand the relation betwen camera images and steering angle.

Since this system takes steering angle decisions by detecting roads and lanes, I would like to call it 'AutoLaneAssist' than 'AutoPilot'. An AutoPilot is supposed to do advanced cruise controll along with lane assist

The system architecture is shown below. Inputs from the camera is processed in the end-to-end system and output steer angles are outputted to the vehicle CANs.
![Nvidia End to End](https://devblogs.nvidia.com/parallelforall/wp-content/uploads/2016/08/inference-624x132.png)

See the Nvidia self driving car in action:
[![Nvidia End to End](https://cdn.onlinewebfonts.com/svg/img_60026.png)](https://www.youtube.com/watch?v=qhUvQiKec2U)



### The system architecture

The training setup is as follow.

![Nvidia End to End](https://devblogs.nvidia.com/parallelforall/wp-content/uploads/2016/08/training-624x291.png)

The layer architecutre of the network is as follow. 
![Nvidia End to End](https://devblogs.nvidia.com/parallelforall/wp-content/uploads/2016/08/cnn-architecture-624x890.png)



### Prototype development
To develop a prototype of the AutoLaneAssist system, we may need a simulated environment - to read the instantaneous camera inputs and to take instantaneous actions. 


<!-- The steps of this project are the following:
- Use the simulator to collect data of good driving behavior
- Design, train and validate a model that predicts a steering angle from image data
- Use the model to drive the vehicle autonomously around the first track in the simulator. The vehicle should remain on the road for an entire loop around the track. -->
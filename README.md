# AutoLaneAssist

>Autonomous cars are going to rule the roads. Why don't we try building a prototype of it.

Autonomous cars are expected to drive from a point to another all by itself. The conventional technologies for self-driving cards are designed to detect roads/lanes and obstacles on it. They use many sensors viz - camera, GPS, IMS etc. From the lane information, another sub module has to calculate the best steering angle and it has to plan its path ahead. Trust me, it is a pretty complicated design.

Researchers in Nvidia developed an end-to-end deep learning system for self-driving cars. Their system reads camera images and outputs steering angle, there by they call it an end-to-end system. They designed a deep CNN network to understand the relation betwen camera images and steering angle.

|The Nvidia research|
|:--------:|
|[![Nvidia End to End](https://devblogs.nvidia.com/parallelforall/wp-content/uploads/2016/08/5Driver-closeup-hands-1200x675-624x351.png)](https://www.youtube.com/watch?v=qhUvQiKec2U)|

#### The Network


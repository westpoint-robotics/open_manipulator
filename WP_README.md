# West Point Instructions for running the Open Manipulator 

## In simulation running in the Podman container on TH1136 computers

- In the host OS clone the repo

  - `cd ~/podman_ws/src`
  - `git clone -b wp_jazzy https://github.com/westpoint-robotics/open_manipulator.git`

- Rebuild the podman image with the updated Dockerfile.

  - `cd /data/EE484/podman`
  - `podman build -t ee484_image .`
  - Then run the container:
  - `/data/EE484/podman/podmanRun_ROS2.sh`
  - Inside the container build the code using the make alias
  - `makews`

- To run headless, change line 129 in open_manipulator_x_bringup/launch/gazebo.launch.py from `False` to `True`

- Start the simulator with the Manipulator  
`ros2 launch open_manipulator_x_bringup gazebo.launch.py`

- Start RVIZ Moveit Plugin  
`ros2 launch open_manipulator_x_moveit_config moveit_gz.launch.py`

- NOTE: as of 24FEB2025 the gripper does not work and generates errors. Any errors related to the gripper can be ignored.

## On Real Hardware

- TODO, test again. Many changes were made for simulation and they may cause problems when running the real hardware.
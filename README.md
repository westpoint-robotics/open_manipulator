# West Point OpenMANIPULATOR-X

## Clone and build the wp_jazzy branch 
   ```bash
      cd ~/${WORKSPACE}/src
      git clone -b wp_jazzy https://github.com/westpoint-robotics/open_manipulator.git

      # Install dependencies
      sudo apt-get update && sudo apt-get upgrade -y
      cd ~/ros2_ws;rosdep update;rosdep install --from-paths src -y --ignore-src

      # Build it
      cd ~/ros2_ws && colcon build --symlink-install
   ```

## Test the Manipulator



# OpenMANIPULATOR-X
<img src="https://github.com/ROBOTIS-GIT/emanual/blob/master/assets/images/platform/openmanipulator_x/OpenManipulator.png">
<img src="https://github.com/ROBOTIS-GIT/emanual/blob/master/assets/images/platform/openmanipulator_x/OpenManipulator_Chain_Capture.png" width="500">

The 4-DOF Open Manipulator-X now supports MoveIt 2, enabling enhanced motion planning and control for advanced robotic applications. This update also brings significant improvements to the teleoperation features, example use cases, and the graphical user interface (GUI), providing a more seamless and user-friendly experience for developers and researchers.

- Active Branches: noetic, humble, main
- Legacy Branches: *-devel

# ROBOTIS e-Manual for OpenMANIPULATOR-X
- [http://emanual.robotis.com/docs/en/platform/openmanipulator/](http://emanual.robotis.com/docs/en/platform/openmanipulator/)

# Open Source related to OpenMANIPULATOR-X
- [open_manipulator](https://github.com/ROBOTIS-GIT/open_manipulator)
- [open_manipulator_y](https://github.com/ROBOTIS-GIT/open_manipulator_y)
- [open_manipulator_p](https://github.com/ROBOTIS-GIT/open_manipulator_p)
- [dynamixel_sdk](https://github.com/ROBOTIS-GIT/DynamixelSDK)
- [dynamixel_workbench](https://github.com/ROBOTIS-GIT/dynamixel-workbench)
- [dynamixel_hardware_interface](https://github.com/ROBOTIS-GIT/dynamixel_hardware_interface)

# Documents and Videos related to OpenMANIPULATOR-X
- [ROBOTIS e-Manual for OpenMANIPULATOR-X](http://emanual.robotis.com/docs/en/platform/openmanipulator/)
- [ROBOTIS e-Manual for OpenMANIPULATOR-P](https://emanual.robotis.com/docs/en/platform/openmanipulator_p/overview/)
- [ROBOTIS e-Manual for DYNAMIXEL SDK](http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)
- [ROBOTIS e-Manual for DYNAMIXEL Workbench](http://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_workbench/)
- [YouTube Play List for OpenMANIPULATOR](https://www.youtube.com/playlist?list=PLRG6WP3c31_WpEsB6_Rdt3KhiopXQlUkb)

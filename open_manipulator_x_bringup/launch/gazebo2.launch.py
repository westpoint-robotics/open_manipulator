# Copyright (C) 2023 Open Source Robotics Foundation
# Copyright (C) 2023 Open Navigation LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is modified from the all-in-one launch script intended for use by nav2 developers."""

import os
import tempfile

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable
from launch.substitutions import LaunchConfiguration, PythonExpression, PathJoinSubstitution

from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit


def generate_launch_description():
    # Get the launch directory
    sim_dir = get_package_share_directory('open_manipulator_x_bringup')
    desc_dir = get_package_share_directory('open_manipulator_x_description')
    launch_dir = os.path.join(sim_dir, 'launch')
    print(f'\n\tsim_dirs: {sim_dir}\n\tdesc_dir: {desc_dir}\n\tlaunch_dir: {launch_dir}')
    print(f'\tmodels path: {os.path.join(sim_dir, 'models')}\n')
    world_file_name = 'empty.world'
    world_path = os.path.join(sim_dir, 'worlds', world_file_name)
    # Create the launch configuration variables
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    joy_config = 'xbox'

    # Launch configuration variables specific to simulation
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_rviz = LaunchConfiguration('use_rviz')
    use_joy = LaunchConfiguration('use_joy')
    use_simulator = LaunchConfiguration('use_simulator')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    headless = LaunchConfiguration('headless')
    world = LaunchConfiguration('world')
    pose = {
        'x': LaunchConfiguration('x_pose', default='0.00'),
        'y': LaunchConfiguration('y_pose', default='0.00'),
        'z': LaunchConfiguration('z_pose', default='0.01'),
        'R': LaunchConfiguration('roll', default='0.00'),
        'P': LaunchConfiguration('pitch', default='0.00'),
        'Y': LaunchConfiguration('yaw', default='0.00'),
    }
    robot_name = LaunchConfiguration('robot_name')
    robot_sdf = LaunchConfiguration('robot_sdf')
    arm_joint_controller = LaunchConfiguration("arm_joint_controller")
    # gripper_joint_controller = LaunchConfiguration("gripper_joint_controller")
    activate_joint_controller = LaunchConfiguration("activate_joint_controller")

    # Map fully qualified names to relative ones so the node's namespace can be prepended.
    # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
    # https://github.com/ros/geometry2/issues/32
    # https://github.com/ros/robot_state_publisher/pull/30
    # TODO(orduno) Substitute with `PushNodeRemapping`
    #              https://github.com/ros2/launch_ros/issues/56
    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace', default_value='', description='Top-level namespace'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='True',
        description='Use simulation (Gazebo) clock if true',
    )

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(sim_dir, 'rviz', 'open_manipulator_x.rviz'),
        description='Full path to the RVIZ config file to use',
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='True',
        description='Whether to start rviz',
    )

    declare_use_joy_cmd = DeclareLaunchArgument(
        'use_joy',
        default_value='True',
        description='Whether to start joystick control nodes',
    )

    declare_use_simulator_cmd = DeclareLaunchArgument(
        'use_simulator',
        default_value='True',
        description='Whether to start the simulator',
    )

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        'use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher',
    )

    declare_simulator_cmd = DeclareLaunchArgument(
        'headless', default_value='False', description='Whether to execute gzclient)'
    )

    # declare_world_cmd = DeclareLaunchArgument(
    #     'world',
    #     default_value=os.path.join(sim_dir, 'worlds', 'depot.sdf'),
    #     description='Full path to world model file to load',
    # )

    declare_world_cmd = DeclareLaunchArgument(
        name='world',
        default_value=world_path,
        description='Full path to the world model file to load',
    )

    declare_robot_name_cmd = DeclareLaunchArgument(
        'robot_name', default_value='manipulatorx', description='name of the robot'
    )

    # TODO Check if we are doing this twice. robot state publisher may also do this? 
    declare_robot_sdf_cmd = DeclareLaunchArgument(
        'robot_sdf',
        default_value=os.path.join(desc_dir, 'urdf', 'open_manipulator_x_robot.urdf.xacro'),
        description='Full path to robot sdf file to spawn the robot in gazebo',
    )

    declare_activate_joint_controller_cmd = DeclareLaunchArgument(
            "activate_joint_controller",
            default_value="true",
            description="Enable headless mode for robot control",
        )
    
    declare_arm_joint_controller_sdf_cmd = DeclareLaunchArgument(
            "arm_joint_controller",
            default_value="arm_controller",
            description="Robot controller to start.",
        )
    
    declare_gripper_joint_controller_sdf_cmd = DeclareLaunchArgument(
            "gripper_joint_controller",
            default_value="gripper_controller",
            description="Robot controller to start.",
        )

    start_robot_state_publisher_cmd = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=namespace,
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time,
             'robot_description': Command(['xacro', ' ', robot_sdf])}
        ],
        remappings=remappings,
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    
    # There may be other controllers of the joints, but this is the initially-started one
    arm_joint_controller_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[arm_joint_controller, "-c", "/controller_manager"],
        condition=IfCondition(activate_joint_controller),
    )
    arm_joint_controller_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[arm_joint_controller, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(activate_joint_controller),
    )

    # gripper_controller_spawner = Node(
    #     package='controller_manager',
    #     executable='spawner',
    #     arguments=[
    #         'gripper_controller',
    #         '--param-file',
    #         ],
    # )    



    # # There may be other controllers of the joints, but this is the initially-started one
    # gripper_joint_controller_spawner_started = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=[gripper_joint_controller, "-c", "/controller_manager"],
    #     condition=IfCondition(activate_joint_controller),
    # )

    # gripper_joint_controller_spawner_stopped = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=[gripper_joint_controller, "-c", "/controller_manager", "--stopped"],
    #     condition=UnlessCondition(activate_joint_controller),
    # )


    # rviz_cmd = Node(
    #     condition=IfCondition(use_rviz),
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     output='screen',
    #     arguments=['-d', rviz_config_file],
    #     parameters=[{'use_sim_time': use_sim_time}],
    #     remappings=[
    #         ('/tf', 'tf'),
    #         ('/tf_static', 'tf_static')
    #     ],
    # )


    # The SDF file for the world is a xacro file because we wanted to
    # conditionally load the SceneBroadcaster plugin based on wheter we're
    # running in headless mode. But currently, the Gazebo command line doesn't
    # take SDF strings for worlds, so the output of xacro needs to be saved into
    # a temporary file and passed to Gazebo.
    world_sdf = tempfile.mktemp(prefix='manipulator_', suffix='.sdf')
    world_sdf_xacro = ExecuteProcess(
        cmd=['xacro', '-o', world_sdf, ['headless:=', headless], world])
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch',
                         'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -s ', world_sdf]}.items(),

        condition=IfCondition(use_simulator))

    remove_temp_sdf_file = RegisterEventHandler(event_handler=OnShutdown(
        on_shutdown=[
            OpaqueFunction(function=lambda _: os.remove(world_sdf))
        ]))

    desc_urdf_path = desc_dir.rsplit('/',1)[0] # get directory for finding tbot3 urdf
    set_env_vars_resources = AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(sim_dir, 'worlds'))
    set_env_vars_resources2 = AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(sim_dir, 'models'))
    set_env_vars_resources3 = AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', desc_urdf_path)
    
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch',
                         'gz_sim.launch.py')
        ),
        condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])),
        launch_arguments={'gz_args': ['-g' ]}.items(),
    )
    
    joystick_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('teleop_twist_joy'),
                         'launch',
                         'teleop-launch.py')
        ),
        condition=IfCondition(use_joy),
        launch_arguments={'joy_config': joy_config,
                          'joy_dev': '0',
                          'enable_button': '4',
                          'use_sim_time': use_sim_time}.items())
                          # enable_button not working above here
    
    gz_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'spawn_manipulator.launch.py')),
        launch_arguments={'namespace': namespace,
                          'use_simulator': use_simulator,
                          'use_sim_time': use_sim_time,
                          'robot_name': robot_name,
                          'robot_sdf': robot_sdf,
                          'x_pose': pose['x'],
                          'y_pose': pose['y'],
                          'z_pose': pose['z'],
                          'roll': pose['R'],
                          'pitch': pose['P'],
                          'yaw': pose['Y']}.items())
    
    gz_camera_mover = ExecuteProcess(
        cmd=[[
            FindExecutable(name='gz'),
            " service -s /gui/move_to/pose ",
            " --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 2000 ",
            " --req 'pose: {position: {x: 0.12, y: -0.75, z: 0.34} orientation: {x: -0.0494374, y: 0.0494767, z: 0.7050942, w: 0.7056559}}' ",
        ]],
        shell=True
    )
    # gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 2000 --req "pose: {position: {x: 0.12, y: -0.75, z: 0.34} orientation: {x: -0.0494374, y: 0.0494767, z: 0.7050942, w: 0.7056559}}"

    # spawn_gripper_controller = RegisterEventHandler(
    #         event_handler=OnProcessExit(
    #             target_action=joint_state_broadcaster_spawner,
    #             on_exit=[gripper_controller_spawner],
    #         )
    #     )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_use_sim_time_cmd)

    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_use_joy_cmd)
    ld.add_action(declare_use_simulator_cmd)
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_simulator_cmd)
    ld.add_action(declare_world_cmd)
    ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_robot_sdf_cmd)
    ld.add_action(declare_activate_joint_controller_cmd)
    ld.add_action(declare_arm_joint_controller_sdf_cmd)
    ld.add_action(declare_gripper_joint_controller_sdf_cmd)

    ld.add_action(set_env_vars_resources)
    ld.add_action(set_env_vars_resources2)
    ld.add_action(set_env_vars_resources3)
    ld.add_action(world_sdf_xacro)
    ld.add_action(remove_temp_sdf_file)
    ld.add_action(gz_robot)
    ld.add_action(gazebo_server)
    ld.add_action(gazebo_client)
    # ld.add_action(joystick_control)
    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(arm_joint_controller_spawner_started)
    ld.add_action(arm_joint_controller_spawner_stopped)
    # ld.add_action(spawn_gripper_controller)
    # ld.add_action(gripper_joint_controller_spawner_started)
    # ld.add_action(gripper_joint_controller_spawner_stopped)

    # Add the actions to launch all of the navigation nodes
    ld.add_action(start_robot_state_publisher_cmd)
    #ld.add_action(rviz_cmd)
    ld.add_action(gz_camera_mover)

    return ld

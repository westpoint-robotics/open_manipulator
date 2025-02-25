import sys
import rclpy
from rclpy.node import Node
from moveit_commander import MoveGroupCommander, RobotCommander, PlanningSceneInterface
from geometry_msgs.msg import Pose

class MoveItDemo(Node):
    def __init__(self):
        super().__init__('moveit_demo')
        rclpy.logging.set_logger_level(
            'moveit_ros_planning_interface', rclpy.logging.LoggingSeverity.WARN
        )
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        self.move_group = MoveGroupCommander("panda_arm") # Replace with your robot's planning group name

    def go_to_pose(self, x, y, z, qx, qy, qz, qw):
        pose_goal = Pose()
        pose_goal.position.x = x
        pose_goal.position.y = y
        pose_goal.position.z = z
        pose_goal.orientation.x = qx
        pose_goal.orientation.y = qy
        pose_goal.orientation.z = qz
        pose_goal.orientation.w = qw
        self.move_group.set_pose_target(pose_goal)
        success = self.move_group.go(wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()
        return success

def main(args=None):
    rclpy.init(args=args)
    demo = MoveItDemo()
    
    # Example usage:
    success = demo.go_to_pose(0.2, 0.0, 0.6, 0.0, 1.0, 0.0, 0.0)
    if success:
      demo.get_logger().info("Successfully moved to target pose!")
    else:
       demo.get_logger().error("Failed to move to target pose.")
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
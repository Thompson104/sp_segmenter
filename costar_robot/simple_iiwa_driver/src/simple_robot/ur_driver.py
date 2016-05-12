
import rospy
import urx

from simple_robot import CostarArm

class CostarUR5Driver(CostarArm):

    def __init__(self,world="/world",
            listener=None,
            traj_step_t=0.1,
            max_acc=1,
            max_vel=1,
            max_goal_diff = 0.02,
            goal_rotation_weight = 0.01,
            max_q_diff = 1e-6):

        rospy.logerr("Not yet implemented!")
        super(CostarIIWADriver, self).__init__(base_link,end_link,planning_group)


    '''
    Send a whole joint trajectory message to a robot...
    that is listening to individual joint states.
    '''
    def send_trajectory(self,traj):

        rate = rospy.Rate(30)
        t = rospy.Time(0)

        stamp = rospy.Time.now().to_sec()
        self.cur_stamp = stamp

        for pt in traj.points[:-1]:
          self.pt_publisher.publish(pt)
          self.set_goal(pt.positions)

          print " -- %s"%(str(pt.positions))
          start_t = rospy.Time.now()

          if self.cur_stamp > stamp:
            return 'FAILURE - preempted'

          rospy.sleep(rospy.Duration(pt.time_from_start.to_sec() - t.to_sec()))
          t = pt.time_from_start

          #while not self.near_goal:
          #  if (rospy.Time.now() - start_t).to_sec() > 10*t.to_sec():
          #      break
          #  rate.sleep()

        print " -- GOAL: %s"%(str(traj.points[-1].positions))
        self.pt_publisher.publish(traj.points[-1])
        self.set_goal(traj.points[-1].positions)
        start_t = rospy.Time.now()

        # wait until robot is at goal
        #while self.moving:
        while not self.at_goal:
            if (rospy.Time.now() - start_t).to_sec() > 3:
                return 'FAILURE - timeout'
            rate.sleep()

        if self.at_goal:
            return 'SUCCESS - moved to pose'
        else:
            return 'FAILURE - did not reach destination'

    '''
    Send a whole sequence of points to a robot...
    that is listening to individual joint states.
    '''
    def send_sequence(self,traj):
        q0 = self.q0
        for q in traj:
            pt = JointTrajectoryPoint(positions=q)
            self.pt_publisher.publish(pt)
            self.set_goal(q)

            #rospy.sleep(0.9*np.sqrt(np.sum((q-q0)**2)))

        if len(traj) > 0:
            self.pt_publisher.publish(pt)
            self.set_goal(traj[-1])
            rate = rospy.Rate(10)
            start_t = rospy.Time.now()

            # wait until robot is at goal
            while not self.at_goal:
                if (rospy.Time.now() - start_t).to_sec() > 10:
                    return 'FAILURE - timeout'
                rate.sleep()

            return 'SUCCESS - moved to pose'

    def handle_mode_tick(self):
        if self.driver_status in mode.keys():
            self.iiwa_mode_publisher.publish(mode[self.driver_status])
        else:
            #rospy.logwarn('IIWA mode for %s not specified!'%self.driver_status)
            pass


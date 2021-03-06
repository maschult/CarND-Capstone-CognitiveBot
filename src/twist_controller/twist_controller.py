import rospy
from pid import PID
import math
from yaw_controller import YawController

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, **kwargs):
        # TODO: Implement

        self.vehicle_mass    = kwargs['vehicle_mass']
        self.fuel_capacity   = kwargs['fuel_capacity']
        self.wheel_radius    = kwargs['wheel_radius']
        self.brake_deadband  = kwargs['brake_deadband']
        self.accel_limit     = kwargs['accel_limit']
        self.decel_limit     = kwargs['decel_limit']
        self.max_steer_angle = kwargs['max_steer_angle']

        self.acceleration_pid = PID(11.2, 0.05, 0.3, self.decel_limit, self.accel_limit)
        self.steer_pid        = PID(0.8, 0.05, 0.2, -self.max_steer_angle/2, self.max_steer_angle/2)
        # calculate braking gain
        self.braking_gain = self.vehicle_mass * self.wheel_radius / 4

        self.last_timestamp = rospy.get_time()

        pass

    def control(self, **kwargs):

        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
        target_steer_angle      = kwargs['target_steer_angle']
        steer_feedback          = kwargs['steer_feedback']
        target_linear_velocity  = kwargs['target_linear_velocity']
        current_linear_velocity = kwargs['current_linear_velocity']
        target_angular_velocity = kwargs['target_angular_velocity']

        '''
        if math.fabs(twist_linear.x) < 0.1:
            twist_linear.x = 0.
        if math.fabs(twist_angular.z) < 0.001:
            twist_angular.z = 0.
        '''

        if self.last_timestamp is not None:
            # Get current time
            time = rospy.get_time()
            # Compute timestep between updates
            dt = time - self.last_timestamp
            #update time stamp
            self.last_timestamp = time

            acc_correction = self.acceleration_pid.step(target_linear_velocity - current_linear_velocity, dt)

            #throttle_gain = 0.12

            if (acc_correction < 0):
                throttle = 0
                # transform the brake command to Nm
                brake = - acc_correction * self.braking_gain
                if brake < self.brake_deadband:
                    brake = self.brake_deadband
                #self.pid_acceleration.reset()
                rospy.loginfo('[speed_controller] Really braking %s', brake)
            else:
                # transforme the throttle commad to mile
                throttle = acc_correction / ONE_MPH
                rospy.loginfo('Throttle PID output %s', throttle)
                brake = 0

            # update steering command
            steering = self.steer_pid.step(target_steer_angle - steer_feedback, dt)

            return throttle, brake, steering
        else:
            return 1., 0., 0.


    def reset(self):
        self.acceleration_pid.reset()
        self.steer_pid.reset()

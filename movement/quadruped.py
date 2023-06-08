from adafruit_servokit import ServoKit
from enum import IntEnum
import math
import bezier
import numpy as np

br_leg_lower_limit = -3
bl_leg_lower_limit = -3

fl_leg_lower_limit = -2.6
fr_leg_lower_limit = -2.5

class Motor(IntEnum):
    # identifies the corresponding pin location with the motor location
    FR_SHOULDER = 0
    FR_ELBOW = 1
    FR_HIP = 2
    FL_SHOULDER = 3
    FL_ELBOW = 4
    FL_HIP = 5
    BR_SHOULDER = 6
    BR_ELBOW = 7
    BL_SHOULDER = 8
    BL_ELBOW = 9

class Quadruped:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        self.upper_leg_length = 10
        self.lower_leg_length = 10.5
        for i in range(10):
            self.kit.servo[i].set_pulse_width_range(500,2500)

    def set_angle(self,motor_id, degrees):
        """
        set the angle of a specific motor to a given angle
        :param motor_id: the motor id
        :param degrees: the angle to put the motor to
        :returns: void
        """
        self.kit.servo[motor_id].angle = degrees

    def rad_to_degree(self,rad):
        """
        Converts radians to degrees
        :param rad: radians
        :returns: the corresponding degrees as a float
        """
        return rad*180/math.pi

    def calibrate(self):
        """
        sets the robot into the default "middle position" use this for attaching legs in right location
        :returns: void
        """
        self.set_angle(Motor.FR_SHOULDER, 60) #0
        self.set_angle(Motor.FR_ELBOW, 90)#0
        self.set_angle(Motor.FR_HIP, 90)#0
        self.set_angle(Motor.FL_SHOULDER, 115)#-5
        self.set_angle(Motor.FL_ELBOW, 90)#0
        self.set_angle(Motor.FL_HIP, 90)#0
        self.set_angle(Motor.BR_SHOULDER, 60)#0
        self.set_angle(Motor.BR_ELBOW, 90)#0
        self.set_angle(Motor.BL_SHOULDER, 115)#-5
        self.set_angle(Motor.BL_ELBOW, 90)    #0
    
    def sit(self):
        """
        sets the robot into the default "middle position" use this for attaching legs in right location
        :returns: void
        """
        self.set_angle(Motor.FR_SHOULDER, 70) #0
        self.set_angle(Motor.FR_ELBOW, 80)#0
        self.set_angle(Motor.FR_HIP, 90)#0
        
        self.set_angle(Motor.FL_SHOULDER, 105)#-5
        self.set_angle(Motor.FL_ELBOW, 100)#0
        self.set_angle(Motor.FL_HIP, 90)#0
        
        self.set_angle(Motor.BR_SHOULDER, 50)#0
        self.set_angle(Motor.BR_ELBOW, 100)#0
        
        self.set_angle(Motor.BL_SHOULDER, 125)#-5
        self.set_angle(Motor.BL_ELBOW, 80)    #0

    def inverse_positioning(self, shoulder, elbow, x, y, z=0, hip=None, right=True):
        '''
        Positions the end effector at a given position based on cartesian coordinates in
        centimeter units and with respect to the shoulder motor of the robot.
        :param shoulder: motor id used for the shoulder
        :param elbow: motor id used for the elbow
        :param x: cartesian x with respect to shoulder motor (forward/back)
        :param y: cartesian y with respect to shoulder motor (up/down)
        :param z: cartesian z with respect to shoulder motor (left/right)
        :param hip: motor id used for the hip
        :param right: a boolean that flips the logic for left and right side to properly map "forward direction"
        :param shoulder_offset: angle offset for the shoulder motor
        :return: a list containing the appropriate angle for the shoulder and elbow
        '''
        L = 2
        y_prime = -math.sqrt((z + L)**2 + y**2)
        thetaz = math.atan2(z + L, abs(y)) - math.atan2(L, abs(y_prime))

        elbow_offset = 20
        a1 = self.upper_leg_length
        a2 = self.lower_leg_length

        c2 = (x**2 + y_prime**2 - a1**2 - a2**2) / (2 * a1 * a2)
        s2 = math.sqrt(1 - c2**2)
        theta2 = math.atan2(s2, c2)
        c2 = math.cos(theta2)
        s2 = math.sin(theta2)

        c1 = (x * (a1 + (a2 * c2)) + y_prime * (a2 * s2)) / (x**2 + y_prime**2)
        s1 = (y_prime * (a1 + (a2 * c2)) - x * (a2 * s2)) / (x**2 + y_prime**2)
        theta1 = math.atan2(s1, c1)

        # Generate positions with respect to robot motors
        theta_shoulder = -theta1
        theta_elbow = theta_shoulder - theta2
        theta_hip = 0

        # Adjust angles based on side
        if right:
            theta_shoulder = 180 - self.rad_to_degree(theta_shoulder)
            theta_elbow = 130 - self.rad_to_degree(theta_elbow) + elbow_offset
            if hip:
                theta_hip = 90 - self.rad_to_degree(thetaz)
        else:
            theta_shoulder = self.rad_to_degree(theta_shoulder) - 5
            theta_elbow = 50 + self.rad_to_degree(theta_elbow) - elbow_offset
            if hip:
                theta_hip = 90 + self.rad_to_degree(thetaz)

        # Set the angles on the motors
        self.set_angle(shoulder, theta_shoulder)
        self.set_angle(elbow, theta_elbow)
        if hip:
            self.set_angle(hip, theta_hip)

        return [theta_shoulder, theta_elbow]

    def leg_position(self, leg_id, x, y, z=0):
        """
        wrapper for inverse position that makes it easier to control each leg for making fixed paths
        :param led_id: string for the leg to be manipulated
        :param x: cartesian x with respect to shoulder motor (forward/back)
        :param y: cartesian y with respect to shoulder motor (up/down)
        :param z: cartesian z with respect to shoulder motor (left/right)
        """
        if leg_id == 'FL':
            self.inverse_positioning(Motor.FL_SHOULDER, Motor.FL_ELBOW, x, y, z=z, hip=Motor.FL_HIP, right=False)
        if leg_id == 'FR':
            self.inverse_positioning(Motor.FR_SHOULDER, Motor.FR_ELBOW, x, y, z=z, hip=Motor.FR_HIP, right=True)
        if leg_id == 'BL':
            self.inverse_positioning(Motor.BL_SHOULDER, Motor.BL_ELBOW, x, y, right=False)
        if leg_id == 'BR':
            self.inverse_positioning(Motor.BR_SHOULDER, Motor.BR_ELBOW, x, y, right=True)
    
    def move(self, controller=None):
        """
        Walks around based on the controller inputted momentum
        :param controller: the controller that is called to determine the robot momentum
        :returns: None, enters an infinite loop
        """
        momentum = np.asarray([0,0,1,0],dtype=np.float32)
        index = 0
        
        # Generate footstep
        s_vals = np.linspace(0.0, 1.0, 20)
        step_nodes = np.asfortranarray([
            [-1.0, -1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0, 1.0],
            [-15.0, -10.0, -13.0, -15.0],
        ])
        curve = bezier.Curve(step_nodes, degree=3)
        step = curve.evaluate_multi(s_vals)
        slide_nodes = np.asfortranarray([
            [1.0, -1.0],
            [1.0, -1.0],
            [-15.0, -15],
        ])
        curve = bezier.Curve(slide_nodes, degree=1)
        slide = curve.evaluate_multi(s_vals)

        motion = np.concatenate((step,slide), axis=1)

        close = False
        while not close:
            momentum, ismoving, sitting = controller(momentum)
            #sprint(momentum)
            if ismoving and not sitting:
                #print("is moving")
                tragectory = motion * momentum[:3, None]
                if momentum[3]:
                    close = True
                x,z,y = tragectory
                #
                i1 = index%40
                i2 = (index+20)%40
                
                # Apply movement based movement
                self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,x[i1],y[i1]+fr_leg_lower_limit,z=z[i1],hip=Motor.FR_HIP,right=True)
                self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,x[i2],y[i2]+br_leg_lower_limit,right=True)
                self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x[i2],y[i2]+fl_leg_lower_limit,z=-z[i2],hip=Motor.FL_HIP,right=False)
                self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,x[i1],y[i1]+bl_leg_lower_limit,right=False)
                index += 1
            
            if not ismoving and not sitting:
                self.calibrate()
                momentum = np.asarray([0,0,1,0],dtype=np.float32)
                
            if sitting and not ismoving:
                self.sit()
                momentum = np.asarray([0,0,1,0],dtype=np.float32)
            
                

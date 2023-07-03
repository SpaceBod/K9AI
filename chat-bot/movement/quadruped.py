from adafruit_servokit import ServoKit
from enum import IntEnum
import math
import bezier
import numpy as np

# Setting height limits for each leg
forward_br_leg_lower_limit = -3.4
forward_bl_leg_lower_limit = -3.35
forward_fl_leg_lower_limit = -3.5
forward_fr_leg_lower_limit = -3.45  

backward_br_leg_lower_limit = -3.5
backward_bl_leg_lower_limit = -3.5
backward_fl_leg_lower_limit = -3.35
backward_fr_leg_lower_limit = -3.4

class Motor(IntEnum):
    # Pins for each servo motor
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
    
    PAN = 14
    TILT = 15

class Quadruped:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        self.upper_leg_length = 10
        self.lower_leg_length = 10.5
        for i in range(10):
            self.kit.servo[i].set_pulse_width_range(500,2500)

    # Helper function to set the angle on a servo motor
    def set_angle(self,motor_id, degrees):
        self.kit.servo[motor_id].angle = degrees

    # Converts radians to degrees
    def rad_to_degree(self,rad):
        return rad*180/math.pi

    # Sets the robot into the default resting position
    def calibrate(self):
        self.set_angle(Motor.FR_SHOULDER, 50)
        self.set_angle(Motor.FR_ELBOW, 90)
        self.set_angle(Motor.FR_HIP, 90)
        self.set_angle(Motor.FL_SHOULDER, 125)#-5
        self.set_angle(Motor.FL_ELBOW, 90)
        self.set_angle(Motor.FL_HIP, 90)
        self.set_angle(Motor.BR_SHOULDER, 50)
        self.set_angle(Motor.BR_ELBOW, 90)
        self.set_angle(Motor.BL_SHOULDER, 125)#-5
        self.set_angle(Motor.BL_ELBOW, 90)
    
    # Adjust the movement of the head for pan and tilt
    def head_control(self, direction, base_position, tilt_position):
        # Adjust the servo positions based on the movement direction
        if direction == "U":
            tilt_position = max(tilt_position - 1, 0)
        elif direction == "D":
            tilt_position = min(tilt_position + 1, 90)
        elif direction == "L":
            base_position = max(base_position - 1, 45)
        elif direction == "R":
            base_position = min(base_position + 1, 135)
        
        self.set_angle(Motor.PAN, base_position)
        self.set_angle(Motor.TILT, tilt_position)
        
        return base_position, tilt_position
        
    # Performs inverse kinematics on each leg
    def inverse_positioning(self, shoulder, elbow, x, y, z=0, hip=None, right=True):
        L = 2
        y_prime = -math.sqrt((z + L)**2 + y**2)
        thetaz = math.atan2(z + L, abs(y)) - math.atan2(L, abs(y_prime))

        elbow_offset = 20
        a1 = self.upper_leg_length
        a2 = self.lower_leg_length

        c2 = (x**2 + y_prime**2 - a1**2 - a2**2) / (2 * a1 * a2)
        square_c2 = (1 - c2**2)
        if (square_c2 < 0):
            s2 = 0
        else:
            s2 = math.sqrt(square_c2)
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
                theta_hip = 92 + self.rad_to_degree(thetaz)

        # Set the angles on the motors
        self.set_angle(shoulder, theta_shoulder)
        self.set_angle(elbow, theta_elbow)
        if hip:
            self.set_angle(hip, theta_hip)

        return [theta_shoulder, theta_elbow]

    # Moves leg to certain position using inverse kinematics
    def leg_position(self, leg_id, x, y, z=0):
        if leg_id == 'FL':
            self.inverse_positioning(Motor.FL_SHOULDER, Motor.FL_ELBOW, x, y, z=z, hip=Motor.FL_HIP, right=False)
        if leg_id == 'FR':
            self.inverse_positioning(Motor.FR_SHOULDER, Motor.FR_ELBOW, x, y, z=z, hip=Motor.FR_HIP, right=True)
        if leg_id == 'BL':
            self.inverse_positioning(Motor.BL_SHOULDER, Motor.BL_ELBOW, x, y, right=False)
        if leg_id == 'BR':
            self.inverse_positioning(Motor.BR_SHOULDER, Motor.BR_ELBOW, x, y, right=True)
    
    # Walks around based on the controller inputted momentum
    def move(self, controller=None, shared_list=None):  
        momentum = np.asarray([0,0,1,0],dtype=np.float32)
        index = 0
        base_position = 90
        tilt_position = 45
        
        # Generate footstep
        s_vals = np.linspace(0.0, 1.0, 20)

        # Define the control points for the dront legs curve
        front_legs_control_points = np.asfortranarray([
            [-0.9, -0.9, 1.2, 1.2],
            [-0.9, -0.9, 1.2, 1.2],
            [-15.6, -11.75, -11.75, -15.6]
        ])

        # Define the control points for the back legs curve
        back_legs_control_points = np.asfortranarray([
            [-0.7, -0.7, 0.7, 0.7], 
            [-0.7, -0.7, 0.7, 0.7],
            [-15.6, -12.1, -12.1, -15.6]
        ])
    
        # Create Bézier curves for the front and back legs
        front_legs_curve = bezier.Curve(front_legs_control_points, degree=3)
        back_legs_curve = bezier.Curve(back_legs_control_points, degree=3)

        front_legs_points = front_legs_curve.evaluate_multi(s_vals)
        back_legs_points = back_legs_curve.evaluate_multi(s_vals)

        slide_nodes = np.asfortranarray([
            [0.3, -0.3],
            [0.3, -0.3],
            [-15.0, -15.0],
        ])
        curve = bezier.Curve(slide_nodes, degree=1)
        slide = curve.evaluate_multi(s_vals)

        motion_f = np.concatenate((front_legs_points,slide), axis=1)
        motion_b = np.concatenate((back_legs_points,slide), axis=1)
        prev_sit_value = False
        close = False

        while not close:
            momentum, forwards, backwards, shared_list, head_dir = controller(momentum, shared_list)

            # Moving forwards
            if forwards and not shared_list[0]:
                tragectory_f = motion_f * momentum[:3, None]
                tragectory_b = motion_b * momentum[:3, None]
                
                if momentum[3]:
                    close = True
                xf,zf,yf = tragectory_f
                xb,zb,yb = tragectory_b
                #
                i1 = index%40
                i2 = (index+20)%40
                
                # Apply movement based movement
                self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,xf[i1],yf[i1]+forward_fr_leg_lower_limit,z=zf[i1],hip=Motor.FR_HIP,right=True)
                self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,xb[i2],yb[i2]+forward_br_leg_lower_limit,right=True)
                self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,xf[i2],yf[i2]+forward_fl_leg_lower_limit,z=-zf[i2],hip=Motor.FL_HIP,right=False)
                self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,xb[i1],yb[i1]+forward_bl_leg_lower_limit,right=False)
                index += 2
            
            # Moving backwards
            if backwards and not shared_list[0]:
                tragectory_f = motion_f * momentum[:3, None]
                if momentum[3]:
                    close = True
                x,z,y = tragectory_f
                #
                i1 = index%40
                i2 = (index+20)%40
                
                # Apply movement based movement
                self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,x[i1],y[i1]+backward_fr_leg_lower_limit,z=z[i1],hip=Motor.FR_HIP,right=True)
                self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,x[i2],y[i2]+backward_br_leg_lower_limit,right=True)
                self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x[i2],y[i2]+backward_fl_leg_lower_limit,z=-z[i2],hip=Motor.FL_HIP,right=False)
                self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,x[i1],y[i1]+backward_bl_leg_lower_limit,right=False)
                index += 1
            
            # IDLE STAND
            if not forwards and not backwards and not shared_list[0]:
                # Set legs to lower limit when not moving and not sitting
                if prev_sit_value == True:
                    self.leg_position("FR", 0, 18.7, z=0)
                    self.leg_position("FR", 0, 18.7, z=0)
                    for value in np.arange(15.0, 18.7, 0.9):
                        self.leg_position("BR", 0, value, z=0)
                        self.leg_position("BL", 0, value, z=0)
                else:
                    self.leg_position("BR", 0, 18.7, z=0)
                    self.leg_position("BL", 0, 18.7, z=0)
                    self.leg_position("FR", 0, 18.7, z=0)
                    self.leg_position("FL", 0, 18.7, z=0)
                momentum = np.asarray([0,0,1,0],dtype=np.float32)
            
            # Check for sit
            if shared_list[0] != prev_sit_value:
                not_sat = False

            # SIT COMMAND
            if shared_list[0] and not forwards and not backwards and not not_sat:
                # Lowers the back legs slowly for smooth descent, whilst rasing front legs slightly
                for value in np.arange(18.7, 15.0, -0.02):
                    if value > 15.8 and value < 16.1:
                        self.leg_position("FR", 0, 19.0, z=0)
                        self.leg_position("FL", 0, 19.0, z=0)
                    if value < 15.2:
                        self.leg_position("FL", 0, 19.3, z=0)
                        self.leg_position("FR", 0, 19.3, z=0)
                    self.leg_position("BR", 0, value, z=0)  # Back leg goes from 18.3 to 15.0
                    self.leg_position("BL", 0, value, z=0)  # Back leg goes from 18.3 to 15.0

                momentum = np.asarray([0,0,1,0],dtype=np.float32)
                not_sat = True
                 
            if head_dir != "":
                base_position, tilt_position = self.head_control(head_dir, base_position, tilt_position)
                
            prev_sit_value = shared_list[0]
            

def raise_head():
    kit = ServoKit(channels=16)
    kit.servo[15].angle = 65
    kit.servo[14].angle = 90

def lower_head():
    kit = ServoKit(channels=16)
    kit.servo[15].angle = 65
    kit.servo[14].angle = 90


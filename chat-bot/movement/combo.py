print("in control_quadruped")

import signal

from adafruit_servokit import ServoKit
from enum import IntEnum
import math
import bezier
import numpy as np
import os

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import time



def handle_interrupt(signal, frame):
    # Function to be executed when Ctrl+C is pressed
    print("Ctrl+C pressed. Running calibrate() before closing...")
    r.calibrate()
    # Exit the program
    exit(0)

def main_quad(queue):
    #print(queue.get())
    r = Quadruped()
    try:
        r.calibrate()
        r.move(controller)
    except KeyboardInterrupt:
        # Ctrl+C was pressed, handle the interrupt
        handle_interrupt(None, None)


#-------------------------------------------------------

#from main import queue

forward_br_leg_lower_limit = -3
forward_bl_leg_lower_limit = -3
forward_fl_leg_lower_limit = -2.6
forward_fr_leg_lower_limit = -2.6

backward_br_leg_lower_limit = -3
backward_bl_leg_lower_limit = -3
backward_fl_leg_lower_limit = -3
backward_fr_leg_lower_limit = -3

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
    
    PAN = 14
    TILT = 15

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
        base_position = 90
        tilt_position = 45
        
        # Generate footstep
        s_vals = np.linspace(0.0, 1.0, 20)
        step_nodes = np.asfortranarray([
            [-1.0, -1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0, 1.0],
            [-15.0, -12.0, -12.0, -15.0],
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
            momentum, forwards, backwards, sitting, head_dir = controller(momentum)
            #print(queue.get())
            #sprint(momentum)
            if forwards and not sitting:
                #print("is moving")
                tragectory = motion * momentum[:3, None]
                if momentum[3]:
                    close = True
                x,z,y = tragectory
                #
                i1 = index%40
                i2 = (index+20)%40
                
                # Apply movement based movement
                self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,x[i1],y[i1]+forward_fr_leg_lower_limit,z=z[i1],hip=Motor.FR_HIP,right=True)
                self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,x[i2],y[i2]+forward_br_leg_lower_limit,right=True)
                self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x[i2],y[i2]+forward_fl_leg_lower_limit,z=-z[i2],hip=Motor.FL_HIP,right=False)
                self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,x[i1],y[i1]+forward_bl_leg_lower_limit,right=False)
                index += 1
            
            if backwards and not sitting:
                #print("is moving")
                tragectory = motion * momentum[:3, None]
                if momentum[3]:
                    close = True
                x,z,y = tragectory
                #
                i1 = index%40
                i2 = (index+20)%40
                
                # Apply movement based movement
                self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,x[i1],y[i1]+backward_fr_leg_lower_limit,z=z[i1],hip=Motor.FR_HIP,right=True)
                self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,x[i2],y[i2]+backward_br_leg_lower_limit,right=True)
                self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x[i2],y[i2]+backward_fl_leg_lower_limit,z=-z[i2],hip=Motor.FL_HIP,right=False)
                self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,x[i1],y[i1]+backward_bl_leg_lower_limit,right=False)
                index += 1
            
            if not forwards and not backwards and not sitting:
                self.calibrate()
                momentum = np.asarray([0,0,1,0],dtype=np.float32)
                
            if sitting and not forwards and not backwards:
                self.sit()
                momentum = np.asarray([0,0,1,0],dtype=np.float32)
                
            if head_dir != "":
                base_position, tilt_position = self.head_control(head_dir, base_position, tilt_position)
            
                
            
                
#------------------------------------------------------------------------

forwards = False
backwards = False
# Initialize pygame
pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Check for connected gamepad controllers
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No gamepad found.")
    quit()

# Select the first gamepad controller
gamepad = pygame.joystick.Joystick(0)
gamepad.init()
print("Gamepad connected:", gamepad.get_name())

# Store the previous state of the left joystick axis
prev_buttons = [False] * gamepad.get_numbuttons()
button_names = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "L_Option",
    5: "Guide",
    6: "R_Option",
    7: "L_Stick",
    8: "R_Stick",
    9: "LB",
    10: "RB",
    11: "UP",
    12: "DOWN",
    13: "LEFT",
    14: "RIGHT"
}

sitting = False

# Main loop
def controller(momentum, accel=0.05, bound=3.5):
    global sitting
    forwards = False
    backwards = False
    head = ""
    pygame.event.pump()
    buttons = [gamepad.get_button(i) for i in range(gamepad.get_numbuttons())]
    for i, button in enumerate(buttons):
        if button and not prev_buttons[i]:
            #print(queue.get())
            print("Button [P]:", button_names[i], i)
            if i == 1:
                sitting = not sitting  # Toggle the sitting value
                #queue.put(sitting)
                print(sitting)
        if not button and prev_buttons[i]:
            print("Button [R]:", button_names[i], i)
        prev_buttons[i] = button

    axes = [gamepad.get_axis(i) for i in range(gamepad.get_numaxes())]
    for i, axis in enumerate(axes):
        if i == 0:  # Check if it's the left joystick axis
            if axis > 0.2:
                direction = "Right"
                momentum[1] = min(momentum[1] + accel, bound)
                forwards = True
            elif axis < -0.2:
                direction = "Left"
                momentum[1] = max(momentum[1] - accel, -bound)
                forwards = True
            else:
                direction = "Center"
        # Right Joystick
        if i == 2:
            if axis > 0.2:
                head = "R"
            elif axis < -0.2:
                head = "L"
        if i == 3:
            if axis > 0.2:
                head = "D"
            elif axis < -0.2:
                head = "U"

            
        elif i == 4 or i == 5:
            if axis > 0.9:
                if i == 4:
                    momentum[0] = min(momentum[0] + accel, bound)
                    forwards = True
                else:
                    momentum[0] = max(momentum[0] - accel, -bound)
                    backwards = True

    pygame.time.wait(10)
    return momentum, forwards, backwards, sitting, head



import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
import numpy as np
from movement.quadruped import Quadruped
import time

forwards = False
backwards = False
# Initialize pygame
#pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Check for connected gamepad controllers
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No gamepad found.")
    #quit()

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


# Main loop
def controller(momentum, sit, accel=0.7, bound=5):
    forwards = False
    backwards = False
    head = ""
    pygame.event.pump()
    buttons = [gamepad.get_button(i) for i in range(gamepad.get_numbuttons())]
    for i, button in enumerate(buttons):
        if button and not prev_buttons[i]:
            print("Button [P]:", button_names[i], i)
            if i == 1:
                sit.value = not sit.value  # Toggle the sitting value
                print(sit.value)
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
                    #print("speed", momentum[0] + accel)
                    momentum[0] = min(momentum[0] + accel, bound)
                    forwards = True
                else:
                    momentum[0] = max(momentum[0] - accel, -bound)
                    backwards = True

    pygame.time.wait(10)
    return momentum, forwards, backwards, sit, head

def command_sit(sit):
    sit.value = True
    print("Sit: ", sit.value)
    
def command_stand(sit):
    sit.value = False
    print("Sit: ", sit.value)

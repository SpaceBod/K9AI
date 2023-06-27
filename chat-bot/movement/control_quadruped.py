print("in control_quadruped")
from movement.game_controller import controller
from movement.quadruped import Quadruped
import signal


def handle_interrupt(signal, frame):
    # Function to be executed when Ctrl+C is pressed
    print("Ctrl+C pressed. Running calibrate() before closing...")
    r.calibrate()
    # Exit the program
    exit(0)

def main_quad(sit):
    r = Quadruped()
    try:
        #r.calibrate()
        r.move(controller, sit)
    except KeyboardInterrupt:
        # Ctrl+C was pressed, handle the interrupt
        handle_interrupt(None, None)

    r = Quadruped()
#     try:
#         r.calibrate()
#         r.move(controller)
#     except KeyboardInterrupt:
#         # Ctrl+C was pressed, handle the interrupt
#         handle_interrupt(None, None)

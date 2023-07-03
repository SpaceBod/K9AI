print("in control_quadruped")
from movement.game_controller import controller
from movement.quadruped import Quadruped

def handle_interrupt(signal, frame, k9):
    # Function to be executed when Ctrl+C is pressed
    print("Ctrl+C pressed. Running calibrate() before closing...")
    k9.calibrate()
    # Exit the program
    exit(0)

def main_quad(shared_list):
    r = Quadruped()
    try:
        #r.calibrate()
        r.move(controller, shared_list)
    except KeyboardInterrupt:
        # Ctrl+C was pressed, handle the interrupt
        handle_interrupt(None, None, r)
    r = Quadruped()

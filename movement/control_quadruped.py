from game_controller import controller
from quadruped import Quadruped
import signal

def handle_interrupt(signal, frame):
    # Function to be executed when Ctrl+C is pressed
    print("Ctrl+C pressed. Running calibrate() before closing...")
    r.calibrate()
    # Exit the program
    exit(0)

if __name__ == "__main__":
    r = Quadruped()
    try:
        r.calibrate()
        r.move(controller)
    except KeyboardInterrupt:
        # Ctrl+C was pressed, handle the interrupt
        handle_interrupt(None, None)

from threading import Thread
import time
import os

from installation import Installation
from messages import State

from audio.audio import RadioFuzzApp
from light.mock_lights import update_lights
from motor.mock_motor import update_motors
from dials.mock_dial import get_dial_values

from motor.control import move_motors, read_dials, MOTORS

dial_values = {
    "a": 1,
    "b": 2,
    "c": 3
}


def convert_motors_to_tuple():
    a = dial_values['a']
    b = dial_values['b']
    c = dial_values['c']

    return (int(a), int(b), int(c))

def listen_for_dial():
    while True:
        dial_values['a'], dial_values['b'], dial_values['c'] = get_dial_values()
        time.sleep(0.1)  # Sleep to prevent this from running too fast

def main():  # Main function
    HOST, PORT = "localhost", 9999  # We have Raspberry PI with ID 92
    installation = Installation(HOST, PORT, id=92, init_state=State.INTERACTIVE)

    # Paths to your audio files
    audio_clip_1 = 'audio/rock.wav'
    audio_clip_2 = 'audio/piano.wav'
    
    # Starting position and solution positions
    initial_position = (50, 50, 50)
    solution1 = (25, 25, 25)
    solution2 = (75, 75, 75)

    # # ------- CORE 1 Audio -------
    # fuzz_app = RadioFuzzApp(audio_clip_1, audio_clip_2, initial_position, solution1, solution2)
    # fuzz_app.start()  # This starts the thread
    dials_thread = Thread(target=read_dials)
    dials_thread.start()

    # ------- CORE 2 Start the network server -------
    server_thread = Thread(target=installation.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # --------- CORE 3 Motors --------
    motor_thread = Thread(target=move_motors)
    motor_thread.start()

    global MOTORS
    

    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            os.system('clear')
            print('--------')
            print(f'Installation state: {State(installation.current_state()).name}')
            print(f'MOTORS values:   {MOTORS}')
            motors_tuple = convert_motors_to_tuple()
            
            
            # update_lights(val_tuple)
            # update_motors(val_tuple)
            #fuzz_app.update_position(val_tuple)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()

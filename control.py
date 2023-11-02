import os
import time
import threading
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
from RPi import GPIO

kit = MotorKit(i2c=board.I2C())
GPIO.setmode(GPIO.BCM)

# Dial A, first from left
dt_A = 18
clk_A = 17
GPIO.setup(clk_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk_A
GPIO.setup(dt_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt_A

# Dial B, 2nd from left
dt_B = 23
clk_B = 22
GPIO.setup(clk_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk_B
GPIO.setup(dt_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt_B

DIAL_A = 0
DIAL_B = 0
MOTOR_A = 0
MOTOR_B = 0

DIAL_BUFFER {
    'a':[],
    'b':[]
}

def convert(dial):
    motor = dial * 8
    return motor

def dial_smooting(dial, signal):
    '''Dial can 'wobble' between clockwise & anticlockwise so this function smoothes
    the changes before they're used as signals for motor movement'''
    global DIAL_BUFFER
    DIAL_BUFFER[dial].append(signal)
    if len(DIAL_BUFFER[dial]) > 3:
        del DIAL_BUFFER[dial]
        if sum(DIAL_BUFFER[dial]) > 1:
            return 1
        elif sum(DIAL_BUFFER[dial]) < 1:
            return -1
        else:
            return 0

def dial():
    global DIAL_A, DIAL_B
    clk_A_last_state = GPIO.input(clk_A)
    clk_B_last_state = GPIO.input(clk_B)
    while True:
        clk_A_state = GPIO.input(clk_A)
        dt_A_state = GPIO.input(dt_A)
        if clk_A_state != clk_A_last_state:
            if dt_A_state != clk_A_state:
                change = dial_smooting('a', 1)
            else:
                change = dial_smooting('a', -1)
            clk_A_last_state = clk_A_state
        DIAL_A += change
        if DIAL_A > 23:
            DIAL_A = 0
        elif DIAL_A < 0:
            DIAL_A = 23

        clk_B_state = GPIO.input(clk_B)
        dt_B_state = GPIO.input(dt_B)
        if clk_B_state != clk_B_last_state:
            if dt_B_state != clk_B_state:
                DIAL_B += 1
                if DIAL_B > 23:
                    DIAL_B = 0
            else:
                DIAL_B -= 1
                if DIAL_B < 0:
                    DIAL_B = 23
            clk_B_last_state = clk_B_state
        time.sleep(0.01)

def motor(interrupt):
    global MOTOR_A, MOTOR_B
    while True:
        os.system('clear')
        print()
        print(f' DIAL_A:  {str(DIAL_A).rjust(3)}')
        print(f' MOTOR_A: {str(MOTOR_A).rjust(3)}')
        print(f' DIAL_B:  {str(DIAL_B).rjust(3)}')
        print(f' MOTOR_B: {str(MOTOR_B).rjust(3)}')

        if MOTOR_A < convert(DIAL_A):
            MOTOR_A += 1
            kit.stepper1.onestep(
                direction=stepper.FORWARD
            )
        elif MOTOR_A > convert(DIAL_A):
            MOTOR_A -=1
            kit.stepper1.onestep(
                direction=stepper.BACKWARD
            )
        if MOTOR_B < convert(DIAL_B):
            MOTOR_B += 1
        elif MOTOR_B > convert(DIAL_B):
            MOTOR_B -=1

        if interrupt.is_set():
            break

def main():
    interrupt = threading.Event()
    motor_thread = threading.Thread(
        target=motor,
        args=(interrupt,)
    )
    motor_thread.start()
    try:
        dial()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
# A small program showing how to implement a
# non-blocking toggle on/off delay on an LED
from machine import Pin
import time

########################################
# CONFIGURATION
pin_led1 = 26                          # The LED pin

duration = 500                         # Duration of LED on/off in ms

########################################
# OBJECTS
led1 = Pin(pin_led1, Pin.OUT)

########################################
# VARIABLES
next_time = 0                          # Non blocking flow control

########################################
# PROGRAM

print("LED1 non blocking symmetric toggle")

while True:
    if time.ticks_diff(time.ticks_ms(), next_time) > 0:
        led1.value(not led1.value())
        next_time = time.ticks_ms() + duration


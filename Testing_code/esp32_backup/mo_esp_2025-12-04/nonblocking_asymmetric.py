# A small program showing how to implement a
# non-blocking asymmetric toggle delay on an LED
from machine import Pin
import time

########################################
# CONFIGURATION
pin_led1 = 26                          # The LED pin

duration_on = 50                       # Duration of LED on in ms
duration_off = 2000                    # Duration of LED off in ms

########################################
# OBJECTS
led1 = Pin(pin_led1, Pin.OUT)

########################################
# VARIABLES
next_time = 0                          # Non blocking flow control

########################################
# PROGRAM

print("LED1 non blocking asymmetric toggle")

while True:
    if time.ticks_diff(time.ticks_ms(), next_time) > 0:
        value = led1.value()
        if value == 1:
            led1.value(0)
            next_time = time.ticks_ms() + duration_off
        else:
            led1.value(1)
            next_time = time.ticks_ms() + duration_on

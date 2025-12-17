from machine import Pin
from time import sleep

motor = Pin(18, Pin.OUT)

motor.value(0)

sleep(1)

motor.value(1)

sleep(2)

motor.value(0)
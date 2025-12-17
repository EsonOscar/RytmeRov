from ina219_lib import INA219
from machine import Pin, I2C, UART, PWM
from time import sleep, ticks_ms
import gc

gc.enable()
gc.collect()

bar = Pin(23, Pin.OUT)
bar.value(0)
uart = UART(2, 9600)
motor = PWM(Pin(18, Pin.OUT), duty=0)


sleep(4)

motor.duty(256)

sleep(6)

motor.duty(0)

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

ina = INA219(i2c)
ina.set_calibration_32V_1A()

start = ticks_ms()

#bar.value(1)
#motor.value(1)
#sleep(0.1)
#motor.value(0)
"""
with open(f"current{str(round(start, 2))}.txt", "a") as f:
    while ticks_ms() - start < 10000:
        f.write(str(ina.get_current()))
        f.write("\n")
        sleep(0.1)

"""

#bar.value(1)
#motor.value(1)
#sleep(2)
#motor.value(0)
#bar.value(0)
    

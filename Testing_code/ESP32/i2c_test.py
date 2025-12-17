from machine import I2C, Pin
from time import sleep

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

while True:
    devices = i2c.scan()
    print([hex(device) for device in devices])
    sleep(1)
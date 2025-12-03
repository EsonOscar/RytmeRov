from time import sleep, ticks_ms
from machine import Pin, SoftI2C
from ads1x15 import ADS1015

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

ads = ADS1015(i2c)

while True:
    print(ads.read(0))
    sleep(0.1)
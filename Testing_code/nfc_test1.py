from machine import Pin, I2C
from time import sleep, ticks_ms

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

devices = i2c.scan()

if len(devices) == 0:
    print("No I2C devices found.")
else:
    print(f"Devices found:\n")
    for i in devices:
        print(f"Device address: 0x{i:02X}")
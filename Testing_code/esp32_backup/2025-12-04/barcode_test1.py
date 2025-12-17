from time import sleep, ticks_ms
from machine import Pin, UART

"""
pwr = Pin(26, Pin.OUT)

pwr.value(1)

sleep(4)

pwr.value(0)
"""

uart = UART(2, 9600)

print("Barcode scanner program successfully loaded, waiting for input...\n")

while True:
    data = uart.readline()
    if data:
        code = data.decode('ascii').strip()
        print(f"Scanned code: {code}")
        data = None
        code = None
    sleep(0.1)

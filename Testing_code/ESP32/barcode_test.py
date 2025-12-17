from machine import Pin, UART
from time import sleep
import gc

#gc.enable()
#gc.collect()

bar = Pin(23, Pin.OUT)
bar.value(0)
uart = UART(2, 9600)

sleep(4)

bar.value(1)

print("Awaiting scan...")
while True:
    data = uart.readline()
    if data:
        try:
            cpr = data.strip().decode("utf-8")
            print(f"\nScanned code: {cpr}\n")
        except UnicodeError as e:
            print("UnicodeError: Expected error, invalid headers recieved")
        except KeyboardInterrupt as e:
            print("Keyboard interrupt, exiting...")
            break
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
    sleep(0.1)

bar.value(0)
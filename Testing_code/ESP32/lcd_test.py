from machine import Pin
from time import sleep
from gpio_lcd import GpioLcd


sleep(2)

#Konfiguration og initialisering af LCD-skærm
lcd = GpioLcd(rs_pin=Pin(4), enable_pin=Pin(15), d4_pin=Pin(2),
              d5_pin=Pin(14), d6_pin=Pin(27), d7_pin=Pin(26),
              num_lines=4, num_columns=20)
lcd.clear()

#LCD status meddelelse ang. netværk
lcd.move_to(0,0)
lcd.putstr("HJERTEFLIMREN FINDER")
lcd.move_to(7,1)
lcd.putstr("X2000")
lcd.move_to(5,3)
lcd.putstr("STARTER...")

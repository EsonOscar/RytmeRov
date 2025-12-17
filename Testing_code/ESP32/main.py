from time import sleep, ticks_ms
from machine import Pin, ADC, I2C, UART, PWM
from ads1x15 import ADS1015
from ina219_lib import INA219
from WiFi import connectPhone, connectPC
from gpio_lcd import GpioLcd
import os
import sys
import uping
import time
import urequests
import tls
import socket
import network
import json
import ntptime
import gc

gc.enable()
gc.collect()

# Function that checks if there is a measurement on the device
def ecg_exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False

# If measurement exists, delete it, to make sure no GDPR protected data is present.
# It gets deleted at the end, but in the case of a crash partway through we make sure
if ecg_exists("ecg.txt"):
    os.remove("ecg.txt")
else:
    pass

# Give the circuit time to start up
sleep(2)

# LCD config and initialization
lcd = GpioLcd(rs_pin=Pin(4), enable_pin=Pin(15), d4_pin=Pin(2),
              d5_pin=Pin(14), d6_pin=Pin(27), d7_pin=Pin(26),
              num_lines=4, num_columns=20)
lcd.clear()

lcd_å = [
  0b00100,
  0b00000,
  0b01110,
  0b10001,
  0b11111,
  0b10001,
  0b10001,
  0b00000
]

lcd_æ = [
  0b01111,
  0b10100,
  0b10100,
  0b11111,
  0b10100,
  0b10100,
  0b10111,
  0b00000
]

lcd_ø = [
  0b10000,
  0b01110,
  0b11001,
  0b10101,
  0b10101,
  0b10011,
  0b01110,
  0b00001
]

# The real order of å,æ and ø. Sweden > Denmark >:)
lcd.custom_char(0, lcd_å)
lcd.custom_char(1, lcd_æ)
lcd.custom_char(2, lcd_ø)

# AD8232 config
lo_min = Pin(34, Pin.IN)
lo_plus = Pin(35, Pin.IN)
sdn = Pin(19, Pin.OUT)
sdn.value(0)

# I2C config
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)

# External ADC config
ads = ADS1015(i2c)

# INA219 Config
ina = INA219(i2c)
ina.set_calibration_32V_1A()

# Vibration motor config
motor = PWM(Pin(18, Pin.OUT), duty=0)

# UART config
uart = UART(2, 9600)

# Barcode scanner config
bar = Pin(23, Pin.OUT)
bar.value(0)

# Welcome message
lcd.move_to(6,0)
lcd.putstr("RYTMEROV")
lcd.move_to(3,1)
lcd.putstr("AFIB SCREENER")
lcd.move_to(5,3)
lcd.putstr(f"STARTER...")

sleep(3)

# Start sundhedskort scan phase
bar.value(1)

# Give the barcode scanner time to start before writing to LCD
# Otherwise the LCD glitches the crap out :<
sleep(1)

lcd.clear()
lcd.move_to(0,0)
lcd.putstr("VENLIGST SCAN DIT")
lcd.move_to(0,1)
lcd.putstr("SUNDHEDSKORT")
lcd.hide_cursor()

start = ticks_ms()
print("Waiting for card scan...")
while True:
    data = uart.readline()
    if data:
        try:
            cpr = data.decode('ascii').strip()
            print(f"Scanned code: {cpr}")
            print(f"Code type: {type(cpr)}")
            data = None
        except UnicodeError as e:
            print("UnicodeError: expected error, invalid headers received")
        try:
            length = len(cpr)
            print(length)
            if length != 10:
                print("Code is not a CPR, try again.")
                raise ValueError("Invalid value")
            code = int(cpr)
            print(f"Code type: {type(code)}")
            print("CPR has been detected.")
            print("Continuuing program...")
            sleep(0.1)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("SUNDHEDSKORT SCANNET")
            sleep(2)
            break
        except ValueError as e:
            print("Code is not a CPR, try again.")
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("SCAN IKKE GODKENDT")
            lcd.move_to(0,1)
            lcd.putstr(f"VENLIGST PR{chr(2)}V IGEN")
            sleep(2)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("VENLIGST SCAN DIT")
            lcd.move_to(0,1)
            lcd.putstr("SUNDHEDSKORT")
            lcd.hide_cursor()
            
        except NameError as e:
            # Happens when invalid headers are received, and the program tries to read the cpr variable
            print(f"NameError: {e}\nExpected error.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("Unexpected error:")
            lcd.move_to(0,1)
            lcd.putstr(e)
            sys.exit()
        
    elif ticks_ms() - start >= 25000:
        print("Time limit reached, exiting...")
        bar.value(0)
        sleep(1)
        lcd.clear()
        lcd.move_to(0,0)
        sleep(0.1)
        lcd.putstr(f"TIDEN ER UDL{chr(2)}BET")
        lcd.move_to(0,1)
        lcd.putstr("PROGRAM AFSLUTTET")
        lcd.move_to(0,3)
        lcd.putstr("SLUK APPARATET")
        sys.exit(1)
        
    sleep(0.1)

sleep(1)

print("\nECG Measurement program successfully loaded.")
print("Measurement beginning in:\n10 seconds...")
lcd.clear()
lcd.move_to(0,0)
lcd.putstr("EKG STARTER OM:")
lcd.move_to(0,1)
lcd.putstr("10 SEKUNDER")
sleep(1)
for i in range(9, 0, -1):
    lcd.move_to(0,1)
    if i > 1:
        lcd.putstr(f"{i} SEKUNDER ")
    else:
        lcd.putstr(f"{i} SEKUND    ")
        sdn.value(1)
    sleep(1)

count = 0
start = ticks_ms()
lcd.clear()
lcd.move_to(0,0)
lcd.putstr("EKG SENSOR AKTIV")
lcd.move_to(0,1)
lcd.putstr("VENLIGST VENTE...")
with open("ecg.txt", "w") as f:
    f.write(f"{cpr}\n")
    cpr = None
    while ticks_ms() - start < 10000:
        t = ticks_ms()
        inp = ads.read(0)
        lop = lo_plus.value()
        lom = lo_min.value()
        f.write(f"{t},{inp},{lom},{lop}\n")              
        count += 1
        #sleep(0.004)

print(f"\nMeasurements taken: {count}\nFrequency: {count / 10}")

sleep(1)

sdn.value(0)

lcd.clear()
lcd.move_to(0,0)
lcd.putstr(f"EKG F{chr(1)}RDIG")
lcd.move_to(0,1)
lcd.putstr("TAK SKAL DU HAVE")

sleep(3)

connection = False
count = 0

lcd.clear()
lcd.move_to(0,0)
lcd.putstr("KOBLER TIL WIFI...")

while not connection:
    try:
        gc.collect()
        wlan = connectPhone()

        print("Client IP:", wlan.ifconfig()[0])
        if wlan.ifconfig()[0] == "0.0.0.0":
            print(f"Connection unsuccessful, attempt: {count+1}\nRetrying...")
            count += 1
            sleep(2)
            pass
        elif count >= 10:
            print("Unable to connect to WiFi, exiting...")
            wlan.disconnect()
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("KUNNE IKKE KOBLE")
            lcd.move_to(0,1)
            lcd.putstr("TIL WIFI, SLUKKER...")
            sleep(3)
            exit()
        elif wlan.ifconfig()[0] != "0.0.0.0":
            print("Connection successful!")
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("FORBINDELSE OPRETTET")
            lcd.move_to(0,1)
            lcd.putstr(f"IP: {wlan.ifconfig()[0]}")
            sleep(3)
            connection = True
    except Exception as e:
        print(f"WiFi error: {e}")
        with open("log.txt", "a") as f:
            f.write(f"Error when connection to WiFi: {e}\n")

timed = False
count = 0
lcd.clear()
lcd.move_to(0,0)
lcd.putstr("SYNKRONISERER INTERN")
lcd.move_to(0,1)
lcd.putstr("SYSTEMTID...")
while not timed:
    try:
        gc.collect()
        year = time.localtime()[0]
        print("\nLocal time before synchronization：%s\n" %str(time.localtime()))
        #ntptime.host = 'time.google.com'
        #ntptime.host = '216.239.35.12'
        #ntptime.host = "pool.ntp.org"
        ntptime.host = "time.cloudflare.com"
        ntptime.timeout = 5
        ntptime.settime()  # Syncs time with an NTP server
        print("\nLocal time after synchronization：%s\n" %str(time.localtime()))
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr("SYNKRONISERET!")
        sleep(3)
        timed = True
    except Exception as e:
        print(f"\nCould not connect to timeserver, error: {e}\n")
        print("Retrying...")
        sleep(2)
        count += 1
        if count >= 10:
            print("Unable to sync time, exiting...")
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr("SYNKRONISERING")
            lcd.move_to(0,1)
            lcd.putstr("FEJLEDE, SLUKKER...")
            sleep(3)
            wlan.disconnect()
            exit()
            

"""
try:
    ping_target = "google.com"
    print(uping.ping(ping_target, count=4, timeout=5000, interval=10, quiet=False, size=64), "\n")
except Exception as e:
    print(f"Error pinging {ping_target}, error: {e}\n")

post_data = {"value": "TEST DATA FROM ESP32"}
body = json.dumps(post_data)
"""

lcd.move_to(0,0)
lcd.putstr("KOBLER TIL")
lcd.move_to(0,1)
lcd.putstr("HVALFANGERNE.COM...")
sleep(3)
server = "hvalfangerne.com"
path = "/api/esp_data"

size = os.stat("ecg.txt")[6]
print(size)



headers = (f"POST {path} HTTP/1.1\r\nHost: {server}\r\nContent-Type: text/plain\r\nContent-Length: {size}\r\nConnection: close\r\n\r\n")

# Load cool hvalfangerne cert :))))
with open("int.cert") as f:
    imcacert = f.read()

# Create SSL context, and load up that awesome cert
ssl = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
ssl.load_verify_locations(imcacert)

# Create SSL socket
try:
    server = "hvalfangerne.com"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = socket.getaddrinfo(server, 443)[0][-1] 
    s.connect(addr)

    ssl_sock = ssl.wrap_socket(s, server_side=False, server_hostname=server)
except Exception as e:
    print(f"Error creating socket, error: {e}\n")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("KOBLING FEJLEDE")
    lcd.move_to(0,1)
    lcd.putstr("SLUKKER...")

lcd.clear()
lcd.move_to(0,0)
lcd.putstr("STREAMER EKG DATA")
lcd.move_to(0,1)
lcd.putstr("TIL SERVER...")
sleep(3)

start = ticks_ms()
# Send HTTPS request
try:
    gc.collect()
    ssl_sock.write(headers.encode())
    chunk_size = 1024
    with open("ecg.txt", "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            #print(chunk)
            if not chunk:
                print("\nStreaming complete\n")
                break
            ssl_sock.write(chunk)
            #sleep(0.001)
    res = ssl_sock.read(2048).decode("utf-8")
except Exception as e:
    print(f"Error sending HTTPS request, error: {e}\n")
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("STREAMING FEJLEDE")
    lcd.move_to(0,1)
    lcd.putstr("SLUKKER...")
    sleep(3)
    sys.exit()
finally:
    try:
        ssl_sock.close()
        s.close()
    except Exception as e:
        print(f"Error closing SSL socket, error: {e}\n")

stop = ticks_ms()

time = (stop - start) / 1000

print(f"Data streaming took {time} seconds")

# Data streaming done, so remove local ECG data
if ecg_exists("ecg.txt"):
    os.remove("ecg.txt")
else:
    pass

lcd.clear()
lcd.move_to(0,0)
lcd.putstr("FJERNER EKG DATA...")
sleep(2)
try:
    gc.collect()
    with open("res.txt", "w") as f:
        f.write(res)
    res = res.strip().split("\n")
    count = 0
    for elem in res:
        #print("****************************************")
        print(elem)
        count += count
except Exception as e:
    print(f"Error reading response, error: {e}\n")
    
#res[count-3] = res[count-3].strip().replace(" ", "")
#res[count-2] = res[count-2].strip().replace(" ", "").replace("t", "T")
#res = f"{res[count-2]}"

#print(res)

#res = dict(res)
    
wlan.disconnect()
print("Disconnected...")

lcd.clear()
lcd.move_to(0,0)
lcd.putstr(f"PROGRAM F{chr(1)}RDIGT")
lcd.move_to(0,1)
lcd.putstr("SLUK APPARAT")

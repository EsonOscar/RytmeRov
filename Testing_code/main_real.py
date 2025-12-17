
from time import sleep, ticks_ms
from machine import Pin, ADC, I2C, UART
from ads1x15 import ADS1015
from WiFi import connectPhone, connectPC
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



red = Pin(18, Pin.OUT)
green = Pin(19, Pin.OUT)
blue = Pin(5, Pin.OUT)
mos = Pin(14, Pin.OUT)
uart = UART(2, 9600)
btn = Pin(32, Pin.IN)



red.value(0)
green.value(0)
blue.value(0)
mos.value(0)

sleep(1)

mos.value(1)

start = ticks_ms()
print("Waiting for card scan...")
while True:
    data = uart.readline()
    if data:
        cpr = data.decode('ascii').strip()
        print(f"Scanned code: {cpr}")
        print(f"Code type: {type(cpr)}")
        data = None
        
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
            mos.value(0)
            green.value(1)
            sleep(1)
            green.value(0)
            break
            
        except Exception as e:
            print("Code is not a CPR, try again.")
            red.value(1)
            sleep(1)
            red.value(0)
        
    elif ticks_ms() - start >= 20000:
        print("Time limit reached, exiting...")
        red.value(0)
        green.value(0)
        blue.value(0)
        mos.value(0)
        sys.exit(1)
        
    sleep(0.1)
    
"""
def ecg_exists(path):
    try:
        os.stat(path)
        red.value(1)
        sleep(1)
        red.value(0)
        return True
    except OSError:
        green.value(1)
        sleep(1)mos = Pin(14, Pin.OUT)
        green.value(0)
        return False

if ecg_exists("ecg.txt"):
    sys.exit()
else:
    pass

"""

red.value(0)
green.value(1)
sleep(1)
green.value(0)

lo_min = Pin(25, Pin.IN)
lo_plus = Pin(26, Pin.IN)

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
ads = ADS1015(i2c)

sdn = Pin(23, Pin.OUT)

sdn.value(0)
sdn.value(1)
print(sdn.value())

print("\nECG Measurement program successfully loaded.")
print("Measurement beginning in:\n10 seconds...")
sleep(1)
red.value(1)
green.value(1)
for i in range(9, 0, -1):
    print(f"{i} seconds...")
    sleep(1)
    red.value(not red.value())
    green.value(not green.value())

red.value(0)
green.value(0)

count = 0
inp = 0
res = []
start = ticks_ms()
blue.value(1)
with open("ecg.txt", "w") as f:
    f.write(f"{cpr}\n")
    cpr = None
    while ticks_ms() - start < 10000:
        t = ticks_ms()
        inp = ads.read(0)
        #inp += 1
        lop = lo_plus.value()
        lom = lo_min.value()
        f.write(f"{t},{inp},{lom},{lop}\n")
        #res.append(f"{t},{inp},{lom},{lop}")        
                
        #print(f"ADC: {inp} | LO-: {lom} | LO+: {lop} | SDN: {sdn.value()}")
        count += 1
        #sleep(0.004)

print(f"\nMeasurements taken: {count}\nFrequency: {count / 10}")

#i2c.deinit()

blue.value(0)
green.value(1)
green.value(0)
sleep(1)

red.value(1)
blue.value(1)
green.value(1)

connection = False
count = 0

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
            exit()
        elif wlan.ifconfig()[0] != "0.0.0.0":
            print("Connection successful!")
            connection = True
    except Exception as e:
        print(f"WiFi error: {e}")
        with open("log.txt", "a") as f:
            f.write(f"Error when connection to WiFi: {e}\n")

timed = False
count = 0
blue.value(0)
green.value(0)
green.value(0)
sleep(0.1)
red.value(0)
blue.value(1)
green.value(1)

while not timed:
    try:
        gc.collect()
        year = time.localtime()[0]
        """
        print(f"Current year: {year}")
        if year == 2025:
            print("Connection successful, continuing program!")
            break
        """
        print("\nLocal time before synchronization：%s\n" %str(time.localtime()))
        #ntptime.host = 'time.google.com'
        #ntptime.host = '216.239.35.12'
        #ntptime.host = "pool.ntp.org"
        ntptime.host = "time.cloudflare.com"
        ntptime.timeout = 5
        ntptime.settime()  # Syncs time with an NTP server
        print("\nLocal time after synchronization：%s\n" %str(time.localtime()))
        
        timed = True
    except Exception as e:
        print(f"\nCould not connect to timeserver, error: {e}\n")
        print("Retrying...")
        sleep(2)
        count += 1
        if count >= 10:
            print("Unable to sync time, exiting...")
            wlan.disconnect()
            exit()
            
blue.value(0)
green.value(0)
green.value(0)
sleep(0.1)
red.value(0)
blue.value(1)
green.value(0)
"""
try:
    ping_target = "google.com"
    print(uping.ping(ping_target, count=4, timeout=5000, interval=10, quiet=False, size=64), "\n")
except Exception as e:
    print(f"Error pinging {ping_target}, error: {e}\n")

post_data = {"value": "TEST DATA FROM ESP32"}
body = json.dumps(post_data)
"""
server = "hvalfangerne.com"
path = "/api/data_test"

size = os.stat("ecg.txt")[6]
print(size)



headers = (f"POST {path} HTTP/1.1\r\nHost: {server}\r\nContent-Type: text/plain\r\nContent-Length: {size}\r\nConnection: close\r\n\r\n")

# Load Intermediate CA certificate
with open("int.cert") as f:
    imcacert = f.read()

# Create SSL client context
ssl = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
ssl.load_verify_locations(imcacert)

# Create socket
try:
    server = "hvalfangerne.com"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = socket.getaddrinfo(server, 443)[0][-1]  # Replace with server IP
    s.connect(addr)

    ssl_sock = ssl.wrap_socket(s, server_side=False, server_hostname=server)
except Exception as e:
    print(f"Error creating socket, error: {e}\n")

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
    res = ssl_sock.read(2048).decode("utf-8")  # Read response
except Exception as e:
    print(f"Error sending HTTPS request, error: {e}\n")
finally:
    try:
        ssl_sock.close()
        s.close()
    except Exception as e:
        print(f"Error closing SSL socket, error: {e}\n")

stop = ticks_ms()

time = (stop - start) / 1000

print(f"Data streaming took {time} seconds")
blue.value(0)
green.value(0)
green.value(0)
sleep(0.1)
red.value(1)
blue.value(1)
green.value(1)

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
red.value(0)
blue.value(0)
green.value(0)

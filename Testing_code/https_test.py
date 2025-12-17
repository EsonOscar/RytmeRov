from WiFi import connectPC, connectPhone
from time import sleep, ticks_ms
import uping
import time
import os
import sys
import urequests
import tls
import socket
import network
import json
import ntptime
import gc

gc.enable()

wlan = connectPhone()


print("Client IP:", wlan.ifconfig()[0])


"""
try:
    print("\nLocal time before synchronization：%s\n" %str(time.localtime()))
    #ntptime.host = 'time.google.com'
    #ntptime.host = '216.239.35.12'
    #ntptime.host = "pool.ntp.org"
    ntptime.host = "time.cloudflare.com"
    ntptime.timeout = 5
    ntptime.settime()  # Syncs time with an NTP server
    print("\nLocal time after synchronization：%s\n" %str(time.localtime()))
except Exception as e:
    print(f"\nCould not connect to timeserver, error: {e}\n")

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
    ssl_sock.write(headers.encode())
    chunk_size = 512
    with open("ecg.txt", "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            print(chunk)
            if not chunk:
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

try:
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
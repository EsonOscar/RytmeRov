from WiFi import connectPC, connectPhone
import uping, ntptime, sys, gc
import time, usocket as socket
from machine import Pin

gc.enable()
gc.collect()

mos = Pin(14, Pin.OUT)
mos.value(0)

wlan = connectPhone()
cfg = wlan.ifconfig()
print("ifconfig:", cfg)
ip, netmask, gateway, dns = cfg

if ip == "0.0.0.0":
    print("No WiFi connection, exiting...")
    sys.exit()

print("Gateway:", gateway, "DNS:", dns)

try:
    print("Pinging gateway...")
    gc.collect()
    print(uping.ping(gateway, count=4, timeout=2000, interval=10, quiet=False, size=16))
except Exception as e:
    print("Error pinging gateway:", e)

try:
    s = socket.socket()
    s.settimeout(5)
    s.connect((gateway, 80))
    print("TCP connect to gateway: OK")
    s.close()
except Exception as e:
    print("TCP connect to gateway failed:", e)

try:
    print("Pinging 8.8.8.8...")
    gc.collect()
    print(uping.ping("8.8.8.8", count=4, timeout=2000, interval=10, quiet=False, size=16))
except Exception as e:
    print("Error pinging 8.8.8.8:", e)

wlan.disconnect()
wlan.active(False)

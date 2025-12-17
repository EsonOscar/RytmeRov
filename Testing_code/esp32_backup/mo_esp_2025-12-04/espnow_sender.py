# https://docs.micropython.org/en/latest/library/espnow.html
import network
import espnow
from machine import Pin, time_pulse_us
import time

# A WLAN interface must be active to send()/recv()
station = network.WLAN(network.STA_IF) # Or network.AP_IF
station.active(True)

esp_now = espnow.ESPNow()
esp_now.active(True)
peer = b'\xB0\xA7\x32\xDD\x6F\x0C'     # MAC address of peer's wifi interface
esp_now.add_peer(peer)                 # Must add_peer() before send()

class HCSR04:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def distance_cm(self):
        # Send a short pulse (10µs) to trigger the measurement
        self.trigger.off()
        time.sleep_us(2)
        self.trigger.on()
        time.sleep_us(10)
        self.trigger.off()

        # Measure the duration of the echo pulse
        pulse_time = time_pulse_us(self.echo, 1, 30000)  # 30ms timeout

        if pulse_time < 0:
            return -1  # No object detected

        # Calculate distance (speed of sound = 34300 cm/s)
        distance = (pulse_time * 0.0343) / 2
        return distance


TRIG_PIN = 5  
ECHO_PIN = 18   

sensor = HCSR04(TRIG_PIN, ECHO_PIN)

while True:
    dist = sensor.distance_cm()
    if dist == -1:
        print("come closer daddy!!")
    else:
        print("Distance:", dist, "cm")
    time.sleep(1)  # Read every second


# Natasha MAC: b'\xB0\xA7\x32\xDD\x6F\x0C'
# EDU MAC: b'\xc8.\x18\x16\xa0\x04'
# PIR MAC: b'\xd4\x8a\xfch\xa3x'
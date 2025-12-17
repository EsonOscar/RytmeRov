# A small program showing how to send a beacon signal using ESP-NOW

# https://docs.micropython.org/en/latest/library/espnow.html
import network, espnow, time

########################################
# CONFIGURATION
rx_mac_addr = b'\xcc\xdb\xa7\x93\x15\x6c' # MAC address of peer's wifi interface. Byte string format1

beacon_interval = 100                  # The beacon signal interval in ms

wifi_2g4_channel = 1                   # The 2,4 GHz Wifi channel 1 to 13

tx_power = 20                          # The transmitting power in dBm from 2 dBm to 21 dBm, real power is -2 to + 0 dB offset

########################################
# OBJECTS
# Wifi
station = network.WLAN(network.STA_IF) # Or network.AP_IF
station.active(True)

# ESP-NOW
esp_now = espnow.ESPNow()
esp_now.active(True)

########################################
# VARIABLES
next_time = 0                          # Non blocking flow control

########################################
# PROGRAM

print("ESP-NOW beacon transmitter")

if station.active():                   # Check if the WLAN is active
    # Set the Wifi channel
    station.config(channel = wifi_2g4_channel)
    ch = station.config('channel')     # Read back the set channel
    print("Wifi channel      : %d" % ch)

    # Set the TX power
    station.config(txpower = tx_power) # 
    pwr = station.config('txpower')    # Read back the set power level
    print("Transmitter power : %d dBm" % pwr)

    # MAC address
    mac_address = station.config("mac") # Returns the MAC address in six bytes
    print("The MAC address is: ", end = "")
    for i in range(5):
        print("%02X:" % mac_address[i], end = "")
    print("%02X" % mac_address[5])     # Print the last byte without the trailing colon

    # ESP-NOW
    esp_now.add_peer(rx_mac_addr)      # Must add_peer() before send()

    esp_now.send(rx_mac_addr, "Starting beacon transmitter") # Info string to receivers
       
    # BEacon transmitting loop
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, next_time) >= 0:
            esp_now.send(rx_mac_addr, str(now), True)
            next_time = now + beacon_interval
            print("Beacon: %d" % now)
        
else:
     print("Wifi is not active")
        
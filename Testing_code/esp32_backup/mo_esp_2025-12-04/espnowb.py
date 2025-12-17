# A small program showing how to receive the RSSI from a beacon signal using ESP-NOW
# https://docs.micropython.org/en/latest/library/espnow.html
import network, espnow

########################################
# CONFIGURATION
wifi_2g4_channel = 1                   # The 2,4 GHz Wifi channel 1 to 13

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

print("ESP-NOW beacon receiver")

if station.active():                   # Check if the WLAN is active
    # Set the Wifi channel
    station.config(channel = wifi_2g4_channel)
    ch = station.config('channel')     # Read back the set channel
    print("Wifi channel      : %d" % ch)

    # MAC address
    mac_address = station.config("mac") # Returns the MAC address in six bytes
    print("The MAC address is: ", end = "")
    for i in range(5):
        print("%02X:" % mac_address[i], end = "")
    print("%02X" % mac_address[5])     # Print the last byte without the trailing colon

    # Receiving ESP-NOW loop
    while True:    
        host, msg = esp_now.recv()
        if msg:                        # msg == None if timeout in recv()
            msg = msg.decode("utf-8")
            print(msg, end = "")
            pt = esp_now.peers_table
            rssi = pt[list(pt.keys())[0]][0]
            print("\t" + str(rssi))    # RSSI = RXed Signal Strength Indicator
        
else:
     print("Wifi is not active")
        
        
# Smart Home ESP-NOW handling functions module
# https://docs.micropython.org/en/latest/library/espnow.html
# https://www.donskytech.com/exploring-esp-now-in-micropython-a-learners-guide/

import network
import espnow

########################################
# OBJECTS
sta = network.WLAN(network.STA_IF)     # Or network.AP_IF
sta.active(True)                       # WLAN interface must be active to send()/recv()

en = espnow.ESPNow()                   # ESP-NOW object
en.active(True)                        # Make ESP-NOW active

########################################
# CONSTANTS
MAC_ADDR_BROADCAST = const(b'\xff\xff\xff\xff\xff\xff') # ESP-NOW broadcast MAC address
                           
########################################
# FUNCTIONS

# Is the MAC address in the list
def esp_now_mac_in_list(mac_addr):
    try:
        en.get_peer(mac_addr)
    except OSError as ose: 
        if ose.args[1] == "ESP_ERR_ESPNOW_NOT_FOUND": 
            return False               # MAC address is not in the list     
    
    return True                        # MAC address is in the list

# Add MAC address to the list of receivers
def esp_now_add_mac_address(mac_addr):
    if esp_now_mac_in_list(mac_addr) == False:
        en.add_peer(mac_addr)          # MAC address is not in the list so add it

# Delete a MAC address from the list of receivers
def esp_now_delete_mac_address(mac_addr):
    try:
        en.del_peer(mac_addr)
    except ValueError:
        print("Failed to delete existing MAC address")    

# Send a message to the receiver with the MAC address
def esp_now_send_message(mac_addr, string):
    try:
        en.send(mac_addr, string, False)
    except ValueError as e:
        print("Error sending the message: " + str(e))    

# Checks if there is a message and if so returns it
def esp_now_receive_message():
    try:    
        host, msg = en.recv(10)              # Check if there is something to receive, 10 ms timeout. Default is 300 s!
        if msg:                            # msg == None if timeout in recv()
            return host, msg
        else:
            return None, None
    
    except ValueError as e:
        print("Error receiving: " + str(e))
        return None, None
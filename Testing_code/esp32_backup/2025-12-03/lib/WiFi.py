# #WIFI Functions

import gc
gc.collect()
import network
from machine import reset
from time import ticks_ms
import secrets
from uthingsboard.client import TBDeviceMqttClient

#Readme function
def readme():
    print("\nFunctions in WiFi.py:")
    
    print("connect()	| Connects to user specified network, from internal network list.")
    print("connectPC()	| Connects to laptop mobile hotspot.")
    print("connectPhone()	| Connects to phone mobile hotspot.")
    print("ifconfig()	| Displays the current ifconfig, and optionally saves it to a dict.")
    print("thingsboard()	| Connects to thingsboard, returns client.")
    print("scan()		| Scans for available WiFi networks, prints resuslts. VERY SKETCHY!\n")

#Connects to the user specified WiFi, returns wifi station
def connect():
    wlan = network.WLAN(network.STA_IF)
    while True:
        choice = 0
        try:
            choice = int(input(f"""Which network would you like to connect to?
Please enter only the number next to the network name:
[1] Latop
[2] Phone
[3] KEA Starlink
[4] Home
Choice: """))
        except:
            pass

        if choice == 1:
            ssid = secrets.SSID.get("Laptop")
            password = secrets.PASSWORD.get("Laptop")
            break
        elif choice == 2:
            ssid = secrets.SSID.get("Phone")
            password = secrets.PASSWORD.get("Phone")
            break
        elif choice == 3:
            ssid = secrets.SSID.get("Starlink")
            password = secrets.PASSWORD.get("Starlink")
            break
        elif choice == 4:
            ssid = secrets.SSID.get("Home")
            password = secrets.PASSWORD.get("Home")
            break
        else:
            print("\nInvalid input, please try again.\n")
        
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print(f'Connecting to network {ssid}...')
            wlan.connect(ssid, password)
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print(f"\nConnected to WiFi: {ssid}")
    return wlan

#Connects to Laptop mobile hotspot, returns wifi station
def connectPC():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print(f'Connecting to network {secrets.SSID.get("Laptop")} ...')
            wlan.connect(secrets.SSID.get("Laptop"), secrets.PASSWORD.get("Laptop"))
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print(f"\nConnected to WiFi: {secrets.SSID.get("Laptop")}\n")
    return wlan

#Connects to IoT WAP, returns WiFi station
def connectIoT():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print(f'Connecting to network {secrets.SSID.get("IoT")} ...')
            wlan.connect(secrets.SSID.get("IoT"), secrets.PASSWORD.get("IoT"))
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print(f"\nConnected to WiFi: {secrets.SSID.get("IoT")}\n")
    return wlan

#Connects to phone mobile hotspot, returns wifi station
def connectPhone():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print(f'Connecting to network {secrets.SSID.get("Phone")}...')
            wlan.connect(secrets.SSID.get("Phone"), secrets.PASSWORD.get("Phone"))
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print(f"\nConnected to WiFi: {secrets.SSID.get("Phone")}\n")
    return wlan

#Connect to home WiFi
def connectHome():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    try:
        if not wlan.isconnected():
            print(f'Connecting to network {secrets.SSID.get("Home")}...')
            wlan.connect(secrets.SSID.get("Home"), secrets.PASSWORD.get("Home"))
            start = ticks_ms()
            while not wlan.isconnected():
                if ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print(f"\nConnected to WiFi: {secrets.SSID.get("Home")}\n")
    return wlan

#Displays the current ifconfig, and optionally saves it to a dict
def ifconfig():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ipDict = {}
    
    ipList = wlan.ifconfig()
    
    #ipDict["SSID"] = ssid
    ipDict["IPv4"] = ipList[0]
    ipDict["SubnetMask"] = ipList[1]
    ipDict["DefaultGateway"] = ipList[2]
    ipDict["DNS"] = ipList[3]
    
    print("ESP32 IP configuration:")
    print(f"IPv4: {ipDict.get("IPv4")}")
    print(f"Subnet Mask: {ipDict.get("SubnetMask")}")
    print(f"Default Gateway: {ipDict.get("DefaultGateway")}")
    print(f"DNS: {ipDict.get("DNS")}\n")
    
    return ipDict

#Connects to thingsboard, returns client
def thingsboard():
    client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)
    client.connect()
    print("\nConnected to Thingsboard, ready to transmit data.")
    return client

#Lokal IoT ubuntu thingsboard
def thingsboardUbuntu():
    client = TBDeviceMqttClient(secrets.SERVERIP.get("ubuntu"), access_token = secrets.SERVERAT.get("IoTTest"))
    client.connect()
    print("\nConnected to Thingsboard, ready to transmit data.\n")
    return client

#Lokal IoT ubuntu thingsboard 2
def thingsboardUbuntu2():
    client = TBDeviceMqttClient(secrets.SERVERIP.get("ubuntu"), access_token = secrets.SERVERAT.get("IoTESP"))
    client.connect()
    print("\nConnected to Thingsboard, ready to transmit data.\n")
    return client

#WiFi scan, lil sketchy
def scan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    authmodes = ["Open", "WEP", "WPA-PSK", "WPA2-PSK4", "WPA/WPA2-PSK"]
    for (ssid, BSSID, channel, RSSI, authmode, hidden) in wlan.scan():
        print("{:s}".format(ssid))
        print("   - Auth: {} {}".format(authmodes[authmode], "(hidden)" if hidden else ""))
        print("   - Channel: {}".format(channel))
        print("   - RSSI: {}".format(RSSI))
        print("   - BSSID: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*BSSID))
        print()
    
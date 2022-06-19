'''
Verbinden des ESP32 in ein Wlan-Netz
Station == Client
'''
import network
from umqtt.simple import MQTTClient
import time

import gc
gc.collect()

#--------------| Konfiguration Wlan |---------------------------
WIFI_ssid = 'SpectreLG'
WIFI_password = '12345678'
#--------------| Konfig Wlan Ende |-----------------------------

#--------------| Konfiguration MQTT |---------------------------
MQTT_Server = '192.168.137.1'
CLIENT_ID = "MQTT_LGA"
#--------------| Konfig MQTT Ende |-----------------------------

#--------------| Aufbau Wlan-Verbindung |-----------------------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Stelle Wlan Verbindung her")
if not wlan.isconnected():
    wlan.connect(WIFI_ssid, WIFI_password)
    while wlan.isconnected() == False:
        pass
    
    print()
    print('Connection successful')
    print(wlan.ifconfig())
    

mqttClient = MQTTClient(CLIENT_ID, MQTT_Server)  

print("Done")

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
WIFI_ssid = 'SPECTRE360DB'
WIFI_password = 'AuaDasTutWLan'
#---------------------------------------------------------------

#--------------| Konfiguration MQTT |---------------------------
MQTT_Server = '192.168.137.1'
CLIENT_ID = "MQTT_BDA"
#---------------------------------------------------------------


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Wlan Verbindung wird hergestellt")
if not wlan.isconnected():
    wlan.connect(WIFI_ssid, WIFI_password)
    while wlan.isconnected() == False:
        pass
    
    print()
    print('Connection successful')
    print(wlan.ifconfig())
    print()

mqttClient = MQTTClient(CLIENT_ID, MQTT_Server)


print("Fertig")

#import extruderUeberwachung
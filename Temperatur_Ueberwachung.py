"""""
Author: Luca Görke
Datum: 17.05.2022
Hardware: ESP32 LILYGO

Während der Lagerung von Filament sollen die Temperatur und die Luftfeuchtigkeit stetig beobachtet werden.
Diese Werte werden über MQTT an NodeRed geliefert und von da aus in eine Datenbank übertragen werden
Übersteigt die Temeperatur 25°C => Lüfter ein bis Temp 20°C erreicht.
Sinkt die Temperatur unter 18°C => Heizspirale ein bis Temp 22°C

Hardware:
HTU2X über I2C (scl = Pin 22, sda = Pin 21)
Rote LED = Pin 26  I  Grüne LED = Pin 27

Version 2 19.06.2022

"""""
#--------------| Importbereich |---------------------------
from pickle import TRUE
import time, json
from machine import Pin, SoftI2C
from boot import mqttClient
from HTU2X import HTU21D

#--------------| Import Ende |-----------------------------

#--------------| MQTT Topics |-----------------------------
MQTT_TOPIC_FILAMENT= "Guntshaus/Filament/Lagerung/Daten"
MQTT_TOPIC_CHARGE= "Guntshaus/Charge/Daten"

#--------------| Topics Ende |------------------------------                      

#--------------| I2C (HTU) Ende |---------------------------
htu = HTU21D(22, 21)

led_Heizspule = Pin(26, Pin.OUT)
led_Lüfter = Pin(27, Pin.OUT)

#--------------| I2C Ende |---------------------------------

#--------------| Hilfsvariablen |---------------------------
bWare = 0
zeitBWare = 0

abkuelen = False
waermen = False

bWareBereich =False
bWareZeitSet = False

uebergabeChargenID = True65
neueID = 0
chargenID = ''
#--------------| Hilfsvariablen Ende |-----------------------

#--------------| Zeitstempel |-------------------------------
oldTime =time.time()
oldTimeMax =10
#--------------| Zeitstempel Ende |---------------------------

#--------------| MQTT Verbindung |----------------------------
try:
    mqttClient.connect()
    print("MQTT-Connected")
except:
    pass


while True:
  #-----Anfrage für die Chargen ID
  if chargenID == '':
    chargenID = str(input("Bitte ChargenID eingeben: ")) # Eingabe der Chargen ID
    neueID = input("Ist die ID neu? JA = 1, Nein =0  ")
    print("Die ChargenID lautet: ", chargenID)
    uebergabeChargenID = False
    bWare = False

  #-----Übergabe der Chargen-Daten an Node-RED
  if uebergabeChargenID == False:
    dataCharge = {
      
      "Charge": {
          "ChargenID" : chargenID,
          "BWare" : bWare,
          "UpdateDatensatz" : neueID
    }
    }
    mqttClient.publish(MQTT_TOPIC_CHARGE, json.dumps(dataCharge))
    print("ID versendet")
    uebergabeChargenID = True

  #-----Ermittlung der Sensorwerte

  humid = round(htu.humidity)
  temp = round(htu.temperature)
  

  humid_string = str(humid)
  temp_string = str(temp)

  #-----Json Filament
  dataFilament ={     
      
        "Filamentbox": {
          "Temperatur" : temp_string,
          "Humidity" : humid_string,
          "ChargenID": chargenID
                   
        }
    }
  
  #-------Abfrage Luftfeuchtigkeit
  
  if humid > 50:
    led_Lüfter.value(1)
    led_Heizspule.value(1)
    bWareBereich = True
  
  elif humid <=50:
    led_Lüfter(0)
    led_Heizspule.value(0)
    bWareBereich = False
  
  #------Abfrage Temperatur
  if temp > 25:
    abkuehlen = True
    led_Lüfter(1)
    bWareBereich = True

  if temp == 20 and abkuehlen == True:
    abkuehlen = False
    led_Lüfter(0)
    bWareBereich = False

  if temp < 18:
    waermen = True
    led_Heizspule(1)
    bWareBereich = True

  if temp == 22 and waermen == True:
    waermen = False
    led_Heizspule(0)
    bWareBereich = False

  #------Abfrage B-Ware
  # Rücksetzen des B-Ware Timers
  if bWareBereich == False:
      bWareZeitSet = False
  
  # Setzen des B-Ware Timers
  if bWareBereich == True and bWareZeitSet == False:
    zeitBWare = time.time()
    bWareZeitSet = not bWareZeitSet

  if time.time() >= (zeitBWare + 15) and bWareBereich == True:
    bWare = 1
  else:
    bWare = 0

  # B-Waren Meldung an Node-RED
  if bWare == 1:
    neueID = 0
    dataCharge = {
      
      "Charge": {
          "ChargenID" : chargenID,
          "BWare" : bWare,
          "UpdateDatensatz" : neueID
      }
    }
    
    dataFilament ={     
      
        "Filamentbox": {
          "Temperatur" : temp_string,
          "Humidity" : humid_string,
          "ChargenID": chargenID
                   
        }
    }
    
        
    mqttClient.publish(MQTT_TOPIC_FILAMENT, json.dumps(dataFilament))
    time.sleep(1)
    mqttClient.publish(MQTT_TOPIC_CHARGE, json.dumps(dataCharge))
    time.sleep(1)
    chargenID = ''
    
  # Übermittlung der Daten an den Broker und Node-RED
  
  if (time.time() >= oldTime + oldTimeMax) and chargenID != '' :
    
    print("Temp:",temp, "Humid:", humid," %", "Chargen ID:", chargenID)

    mqttClient.publish(MQTT_TOPIC_FILAMENT, json.dumps(dataFilament))

    oldTime=time.time()

    time.sleep(5)
    
  
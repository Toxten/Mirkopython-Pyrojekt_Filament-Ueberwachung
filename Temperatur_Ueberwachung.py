"""""
Author: Luca Görke
Datum: 17.05.2022
Hardware: ESP32 LILYGO

Während der Lagerung von Filament sollen die Temperatur und die Luftfeuchtigkeit stetig beobachtet werden.
Diese Werte werden über MQTT an NodeRed geliefert und von da aus in eine Datenbank übertragen werden
Übersteigt die Temeperatur 25°C => Lüfter ein bis Temp 20°C erreicht.
Sinkt die Temperatur unter 18°C => Heizspirale ein bis Temp 22°C

HTU2X über I2C (scl = Pin 22, sda = Pin 21)
Rote LED = Pin 26  I  Grüne LED = Pin 27

Version 0 17.05.2022

Kundenauftrag fertig bis Freitag als Mail
Abgabe ist 10.06
"""""
import time, json
from machine import Pin, SoftI2C
from boot import mqttClient
from HTU2X import HTU21D


MQTT_TOPIC = "Guntshaus/Filament/Lagerung/Daten"

# I2C für Sensorik deklarieren
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))                        

htu = HTU21D(22, 21)

led_Heizspule = Pin(26, Pin.OUT)
led_Lüfter = Pin(27, Pin.OUT)

abkuelen = False
waermen = False
test =True

# Erstellen des Zeitstempels
oldTime =time.time()
oldTimeMax =10

try:
    mqttClient.connect()
    print("MQTT-Connected")
except:
    pass


while True:

  
  humid = round(htu.humidity)
  temp = round(htu.temperature)
  

  humid_string = str(humid)
  temp_string = str(temp)

  
  #-------Abfrage Luftfeuchtigkeit
  
  if humid > 50:
    led_Lüfter.value(1)
    led_Heizspule.value(1)
  
  elif humid <=50:
    led_Lüfter(0)
    led_Heizspule.value(0)
  
  #------Abfrage Temperatur
  if temp > 25:
    abkuehlen = True
    led_Lüfter(1)
  
  if temp == 20 and abkuehlen == True:
    abkuehlen = False
    led_Lüfter(0)

  if temp < 18:
    waermen = True
    led_Heizspule(1)

  if temp == 22 and waermen == True:
    waermen = True
    led_Heizspule(1)

  
  dataFilament ={     
      
        "Filamentbox": {
          "Temperatur" : temp_string,
          "Humidity" : humid_string
                   
        }
    }

   
  
  if time.time() >= oldTime + oldTimeMax:
    
    print("Temp:",temp, "Humid:", humid," %")

    mqttClient.publish(MQTT_TOPIC, json.dumps(dataFilament))

    oldTime=time.time()

    time.sleep(5)
    
  
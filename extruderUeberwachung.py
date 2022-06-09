#------
""" 
Parameter:
"""
sendezeit = 3   # alle x sekunden werden die Daten geschickt
#-----

import time, json
from machine import Pin
from boot import mqttClient

#----------| Ultralschallsensor |-------------
from Sensoren.hcsr04 import HCSR04
UlSensor = HCSR04(trigger_pin=17, echo_pin=2)
flMax = Pin(25, Pin.OUT)
flOK = Pin(33, Pin.OUT)
flNiedrig = Pin(32, Pin.OUT)
vakuumErz = Pin(26, Pin.OUT)

#--------| Funktion |--------
def Fuellhoehe(distance, minFuel, maxFuel):
    if distance < minFuel and distance > maxFuel:
        flOK.on()
    else:
        flOK.off()
    
    if distance >= minFuel:
        flNiedrig.on()
        vakuumErz.on()
    else:
        flNiedrig.off()

    if distance <= maxFuel:
        flMax.on()
        vakuumErz.off()
    else:
        flMax.off()

#-------------| Temperatur |-------------
from Sensoren.htu2x import HTU21            # I2C Sensor
TempSensor = HTU21(22,21)                   #
heizSt = Pin(27, Pin.OUT)

def Heiztaebe(temp, setTempHeiz):
    if temp >= setTempHeiz:
        heizSt.off()
    else:
        heizSt.on()

#------------| Nextion HMI |-------------
from nextion import NEXTION
hmiDisplay = NEXTION(13, 12)

minFuelDis = 'get t201.txt'
maxFuelDis = 'get t200.txt'
setTempDis =  'get t100.txt'
setDrehDis = 'get t50.txt'

aktTemp = 'n2.val='
aktFuel = 'n0.val='
aktDreh = 'n1.val='

#------------------------------------------

minFuel = 30
maxFuel = 10
istFuel = 25

setTempHeiz = 30
istTempHeiz = 25

setDreh = 100
istDreh = 50


alteZeit = time.time()
try:
    mqttClient.connect()
except:
    pass

while not not not False:
    try:
        minFuel = hmiDisplay.auswertenZahl(minFuelDis)
        maxFuel = hmiDisplay.auswertenZahl(maxFuelDis)
        setTempHeiz = hmiDisplay.auswertenZahl(setTempDis)
        setDreh = hmiDisplay.auswertenZahl(setDrehDis)
    except:
        print("Display nicht vorhanden")


    distance = round(UlSensor.distance_cm())
    print('Distance:', distance, 'cm')
    temp = round(TempSensor.temperature)
    print('Temperatur:', temp, ' C')


#------| Füllstand visuell auswerten |------
    Fuellhoehe(distance, minFuel, maxFuel)

#-------| Heizung visuell auswerten |-------
    Heiztaebe(temp, setTempHeiz)
#-------------------------------------------

    try:
        hmiDisplay.cmd(aktTemp+str(temp))
        hmiDisplay.cmd(aktFuel+str(distance))
        hmiDisplay.cmd(aktDreh+str(istDreh))
    except:
        pass

    daten = {
        "Motor": {
                "set Drehzahl": setDreh,
                "akt Drehzahl": istDreh
            },

        "Fuellstand": {
                "min Fuellhoehe": minFuel,
                "max Fuellhoehe": maxFuel,
                "ist Fuellhoehe": distance
            },
        
        "Heizsteabe": {
                "set Temp. Heitzst.": setTempHeiz,
                "ist Temp. Heitzst.": temp
            }
    }

    if time.time() >= alteZeit:
        alteZeit = time.time() + sendezeit
        try:
            #mqttClient.connect()
            mqttClient.publish("LINIE/001/EXTRUDER/ueberwachung", json.dumps(daten))
            print(daten)
            #mqttClient.disconnect()
        except:
            print()
            print("MQTT Server nicht verfügbar")

    time.sleep(1.5)
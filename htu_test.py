import time
from machine import Pin, SoftI2C
from HTU2X import HTU21D



i2c = SoftI2C(scl=Pin(22), sda=Pin(21)) 

htu = HTU21D(22, 21)


humid = round(htu.temperature)


led_Heizspule = Pin(26, Pin.OUT)
led_Lüfter = Pin(27, Pin.OUT)

led_Heizspule(1)
time.sleep(2)
led_Lüfter(1)
time.sleep(2)
led_Heizspule(0)
time.sleep(2)
led_Lüfter(0)
time.sleep(2)

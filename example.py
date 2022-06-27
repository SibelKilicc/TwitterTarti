#! /usr/bin/python2

import time
import sys
import urllib,urllib2

Max_weight=0 
Min_T_between_Send=60
BASE_URL='https://thingspeak.com/apps/thingtweets'
KEY ='WS29MT2P0H2WOHEC'

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6) //5 ve 6. GPIO pinlerinin ayarlanması

hx.set_reference_unit(862) //Kalibrasyon için ayarlanan referans değeri
#hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Agirlik ekleyebilirsiniz... ")

def send_notification(val):
status= 'Olculen agirlik=' + val
data = urllib.urlencode({'api_key' : KEY, 'status': status})
response = urllib2.urlopen(url=BASE_URL, data=data)
print(response.read())

while True:
    try:

        val = hx.get_weight(1) //Yük sensörü 1kg olduğu için parantez içini 1 olarak yazıyoruz
        print(val g)

        if val > Max_weight:
            print("Dogru secim! Urun agirligi")
            send_notification(val)
            print("Bildirim yok: "+ str(Min_T_between_Send) + "mins")
            time.sleep(Min_T_between_Send* 60)
       
        hx.power_down()
        hx.power_up()
        time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
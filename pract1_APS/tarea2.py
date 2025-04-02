from machine import Pin
import time

pin_led13 = Pin(13, Pin.OUT)
pin_boton2 =Pin(2, Pin.IN)
v = 0
cnn = 0
while True:
    if pin_boton2.value()==1:
        v=not(v)
        time.sleep(1)
    if v == 1:
        cnn=not(cnn)
        pin_led13.value(cnn)
        time.sleep(1)
    else:
        pin_led13.value(0)


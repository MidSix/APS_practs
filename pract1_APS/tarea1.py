from machine import Pin
import time

pin_led = Pin(13, Pin.OUT)
cnn = 0 
while True:
        cnn = not(cnn)
        pin_led.value(cnn)
        time.sleep(1)
        
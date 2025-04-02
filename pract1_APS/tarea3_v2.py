import time
from machine import Pin, ADC

adc = ADC(Pin(33))
adc.atten(ADC.ATTN_6DB)
v_ref = 2

while True:
    adc_val = adc.read()
    print(adc_val)
    v = (adc_val * v_ref) / 4095 # simplemente es despejar la fórmula del adc.
    print(v)
    time.sleep(0.1)


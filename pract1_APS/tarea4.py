import time
from machine import Pin, ADC

adc = ADC(Pin(33))
adc.atten(ADC.ATTN_11DB)
v_ref = 3.3
R = 10000
Rmax=0
while True:
    adc_val =  adc.read()
    print(adc_val)
    v = (adc_val * v_ref) / 4096 # simplemente es despejar la fórmula del adc.
    print(v)
    Rl = (v_ref * R) / v - R
    if Rl>Rmax:
        Rmax=Rl
    print(Rl)
    print(f"R max={Rmax}")
    time.sleep(0.1)


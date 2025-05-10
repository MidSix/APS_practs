import time

from ulab import numpy as np
from ulab import utils
from machine import I2S, Pin

import net
import profiler

N_SAMPLES = const(2048)
SSID = b'Avatel-gF3P'
PWD = b'C6VsKk2B'

net = net.Net(SSID, '', PWD)
profiler = profiler.Profiler()
buffer = bytearray([])
while True:
    sample_rate, duration, h = net.get_params()
    filter_coefficients = len(h)    
    print(f'Solicitud: fs={sample_rate}Hz; t={duration}s; h=[{h[0]}...] ({len(h)} taps)')

    sck_pin = Pin(15)
    ws_pin =  Pin(2)
    sd_pin =  Pin(13)
    
    i2s = I2S(0,
               sck=sck_pin, ws=ws_pin, sd=sd_pin,
               mode=I2S.RX,
               bits=32,
               format=I2S.MONO,
               rate=sample_rate,
               ibuf=N_SAMPLES*4*2)
    
    process_buf = bytearray((N_SAMPLES*4))
    n_muestras_capturar = duration * sample_rate
    n_bytes_leidos = 0
    n_muestras_leidas = 0
    
    time.sleep(1)

    print("==========  COMENZANDO GRABACIÓN ==========")
    
    while True:
        
        t0 = time.ticks_us()
        n_bytes_leidos = i2s.readinto(process_buf)
        t1 = time.ticks_us()
        n_muestras_leidas += (n_bytes_leidos // 4)   
        signal = utils.from_int32_buffer(process_buf)
        signal = np.array(signal / 2**15)
        signal = np.convolve(signal , h)
        t2 = time.ticks_us()
        signal = signal[: -(filter_coefficients - 1)]
        signal = np.array(signal, dtype = np.int16)
        net.send(signal)
        t3 = time.ticks_us()
        profiler.print_partial(t0, t1, t2, t3)
        for byte in range(16):
            print(f"Byte {byte}: {process_buf[byte]}", end=" ")
        print()
        
        if n_muestras_capturar <= n_muestras_leidas:
            break
    print("Average:")
    profiler.print_average()
    print("==========  GRABACIÓN FINALIZADA ==========")
    profiler.print_average()
    net.close()



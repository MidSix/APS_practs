import time

from ulab import numpy as np
from ulab import utils
from machine import I2S, Pin

import net
import profiler

def identify_frequence(index1,index2):
    if signal_spectrogram[index1] > umbral:
        led1.value(1)
                
    if signal_spectrogram[index2] > umbral:
        led2.value(1)

#N_SAMPLES = const(2048) no necesario

SSID = b'Avatel-gF3P'
PWD = b'C6VsKk2B'

net = net.Net(SSID, '', PWD)
profiler = profiler.Profiler()
buffer = bytearray([])

FREC1 = const(400)
FREC2 = const(422)
umbral = 10000
sck_pin = Pin(15)
ws_pin =  Pin(2)
sd_pin =  Pin(13)
led1   =  Pin(26, Pin.OUT)
led2   =  Pin(25, Pin.OUT)
while True:
    sample_rate, bsize, h = net.get_params()
    bin_indice1 = (FREC1*bsize)//sample_rate
    bin_indice2 = (FREC2*bsize)//sample_rate
    filter_coefficients = len(h)
    print(filter_coefficients)
    print(f'Solicitud: fs={sample_rate}Hz; buffer_size={bsize}s; h=[{h[0]}...] ({len(h)} taps)')
    
    i2s = I2S(0,
               sck=sck_pin, ws=ws_pin, sd=sd_pin,
               mode=I2S.RX,
               bits=32,
               format=I2S.MONO,
               rate=sample_rate,
               ibuf=bsize*4*2)
    
    process_buf = bytearray((bsize * 4))
    #n_muestras_capturar = duration * sample_rate / no necesario
    #n_bytes_leidos = 0 / no necesario
    #n_muestras_leidas = 0 / no necesario
    
    time.sleep(1)

    print("==========  COMENZANDO GRABACIÓN ==========")
    previous_last_samples = np.zeros(filter_coefficients - 1)
    while True:
        led1.value(0)
        led2.value(0)
        t0 = time.ticks_us()
        
        #n_bytes_leidos = i2s.readinto(process_buf) no se necesita los bytes que retorna readinto
        
        i2s.readinto(process_buf)
        t1 = time.ticks_us()
        
        #n_muestras_leidas += (n_bytes_leidos // 4) no se necesita
        
        signal = utils.from_int32_buffer(process_buf)
        signal = np.array(signal / 2**15)
        
        if filter_coefficients == 1:
            signal = np.convolve(signal,h)
            t2 = time.ticks_us()
            signal_spectrogram = utils.spectrogram(signal)
            t3 = time.ticks_us()
            profiler.print_partial(t0, t1, t2, t3)
            
            identify_frequence(bin_indice1,bin_indice2)
                
            if net.send(signal_spectrogram) == 0:
                break
            continue
        
        temp = signal.copy()
        signal = np.concatenate((previous_last_samples, signal))
        signal = np.convolve(signal , h)
        t2 = time.ticks_us()
        signal = signal[filter_coefficients - 1: -(filter_coefficients - 1)]
        previous_last_samples = temp[-(filter_coefficients - 1):]
        
        #signal = np.array(signal, dtype = np.int16) / no necesario
        #net.send(signal) cambiamos lo que se le envia a send
        signal_spectrogram = utils.spectrogram(signal)
        t3 = time.ticks_us()
        profiler.print_partial(t0, t1, t2, t3)
        
        identify_frequence(bin_indice1,bin_indice2)
            
        for byte in range(16):
            print(f"Byte {byte}: {process_buf[byte]}", end=" ")
        print()
        if net.send(signal_spectrogram) == 0:
            led1.value(0)
            led2.value(0)
            break
        
        #if n_muestras_capturar <= n_muestras_leidas: no se necesita
            #break
        
    print("Average:")
    profiler.print_average()
    print("==========  GRABACIÓN FINALIZADA ==========")
    profiler.print_average()
    net.close()




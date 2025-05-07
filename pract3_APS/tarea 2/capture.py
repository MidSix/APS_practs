#!/usr/bin/env python

import sys
import socket
import ipaddress
import numpy as np

PORT = 80
N_SAMPLES = 2048


IP='192.168.18.206'  # configurar al valor impreso por el ESP32
SAMPLE_RATE=8000  # en Hz
DURATION=5  # en segundos
FILTER=np.array([1.0], dtype='float32')  # por defecto una delta (dtype debe ser float32!)
OUT='1.wav'  # fichero de salida con el audio


def wav_header(hz, ch, bps, time):
    """This seems to create the structure for the .wav file
        Several lines description:
        
        parameters
        --------------------------
        
        hz : int
            The frequency (hertz).
        ch : int
            channel. 1 for mono and 2 for stereo.
        bps : int
            Bits per sample.
        time: int
            The duration of the record.
            
        returns
        --------------------------
        o.

    """
    
    bytes_per_sample = ch * bps // 8 # (bits per sample // 8) means bytes por sample, and then multiply by the number of channels in which the bytes must go
    bytes_per_second = hz * bytes_per_sample
    data_size = bytes_per_second * time #(4 seconds sending 4 bytes per second means 16bytes sent. Just and example)
    #Toda esta cosa es para darle a los bytes el formato .wav que tendra el archivo de audio
    #--------------------------------------------
    o = bytes("RIFF", "ascii")
    o += (data_size + 36).to_bytes(4, "little")
    o += bytes("WAVE", "ascii")
    o += bytes("fmt ", "ascii")
    o += (16).to_bytes(4, "little")
    o += (1).to_bytes(2, "little")  # 1 = PCM
    o += ch.to_bytes(2, "little")
    o += hz.to_bytes(4, "little")
    o += bytes_per_second.to_bytes(4, "little")
    o += bytes_per_sample.to_bytes(2, "little")
    o += bps.to_bytes(2, "little")
    o += bytes("data", "ascii")
    o += (data_size).to_bytes(4, "little")
    #--------------------------------------------
    return o

### main
def main():
    try:
        ipaddress.ip_address(IP)
    except:
        print(f'IP {IP} inválida')
        return 1

    if SAMPLE_RATE < 8000 or SAMPLE_RATE > 48000:
        print(f'Tasa de muestreo {SAMPLE_RATE} inválida, debe estar en [8000...48000]')
        return 1
        
    if DURATION < 0 or DURATION > 30:
        print(f'Duración {DURATION} inválida, debe estar en [0...30]')
        return 1

    if len(FILTER) > 64 or FILTER.dtype != np.float32:
        print(f'Filtro {FILTER} inválido, debe ser un array de tamaño <= 64 de tipo float32')
        return 1

    try:
        f = open(OUT, 'wb')
    except:
        print(f'cannot open file {OUT}')
        return 1

    # conectamos a la IP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))

    # enviamos la solicitud
    msg = bytearray()
    msg += (4 + 4 + 4 + 4 * len(FILTER)).to_bytes(4, 'little')
    msg += SAMPLE_RATE.to_bytes(4, 'little')
    msg += DURATION.to_bytes(4, 'little')
    msg += FILTER.tobytes()
    s.send(msg)
    
    # recibimos los paquetes y los guardamos en OUT
    i = 0
    f.write(wav_header(SAMPLE_RATE, 1, 16, DURATION))
    while True:
        data = s.recv(N_SAMPLES)
        if not data: 
            break
        data_str = ' '.join('{:02x}'.format(x) for x in data[0:8])
        print(f'{i} {len(data)}: {data_str}')
        i = i + len(data)
        f.write(data)
    f.close()
    s.close()

if __name__ == '__main__':
#El value de la key "__name__" dentro del namespace global es "__main__"
#cuando el programa se ejecuta como modulo principal. (se puede ver el namespace del scope global printeando globals()).
#Lo que significa que el cuerpo de este condicional solo se ejecuta cuando estemos cargando
#este modulo como principal.
    sys.exit(main())
    #Aqui se ejecuta main() y luego se ejecuta sys.exit que termina
    #la ejecucion, dependiendo de lo que devuelva main() [1,0] sabra que
    #hubo error o no.
  



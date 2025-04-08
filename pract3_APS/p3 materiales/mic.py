import time

from ulab import numpy as np
from ulab import utils
from machine import I2S

import net
import profiler

# tamaño de cada bloque
N_SAMPLES = const(2048)
# wifi 
SSID = b'CONFIGURAR'
PWD = b'CONFIGURAR'

net = net.Net(SSID, '', PWD)
profiler = profiler.Profiler()

# bucle principal
while True:
    # queda en espera de los parámetros de captura a través de la red
    sample_rate, duration, h = net.get_params()
    print(f'Solicitud: fs={sample_rate}Hz; t={duration}s; h=[{h[0]}...] ({len(h)} taps)')

    # inicializa I2S
    # ... COMPLETAR ...
    
    # descarta los primeros instantes (ruido)
    time.sleep(1)

    print("==========  COMENZANDO GRABACIÓN ==========")
    
    # bucle de lectura y procesado
    # ... COMPLETAR ...

    print("==========  GRABACIÓN FINALIZADA ==========")
    profiler.print_average()
    
    net.close()


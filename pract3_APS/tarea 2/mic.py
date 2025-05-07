import time

from ulab import numpy as np
from ulab import utils
from machine import I2S, Pin

import net
import profiler

# tamaño de cada bloque
N_SAMPLES = const(2048) #Nuestro buffer de procesamiento debe ser al menos el doble. O sea, 4096 muestras.
#Cada muestra tiene 4 bytes, por lo tanto el total serían 16384 bytes.
# wifi 
SSID = b'Avatel-gF3P'
PWD = b'C6VsKk2B'

net = net.Net(SSID, '', PWD)
profiler = profiler.Profiler()
buffer = bytearray([])
# bucle principal
while True:
    # queda en espera de los parámetros de captura a través de la red
    sample_rate, duration, h = net.get_params()
    print(f'Solicitud: fs={sample_rate}Hz; t={duration}s; h=[{h[0]}...] ({len(h)} taps)')
    # ... COMPLETAR ...
    # inicializa I2S
    sck_pin = Pin(15)    # Serial clock output
    ws_pin =  Pin(2)     # Word clock output
    sd_pin =  Pin(13)    # Serial data output
    
    i2s = I2S(0,
               sck=sck_pin, ws=ws_pin, sd=sd_pin,
               mode=I2S.RX,
               bits=32,
               format=I2S.MONO,
               rate=sample_rate,
               ibuf=N_SAMPLES*4*2)
    
    process_buf = bytearray((N_SAMPLES*4)) #A esta vaina le pasamos como input el int 8192, vale. Lo que va a hacer es convertir ese número en un
    #array de bytes, o sea, va a crear un array con 8192 bytes completamente vacíos, nosotros los llenaremos después con i2s.readinto() porque
    #ese método dentro de su implementación modifica este array copiándole los elementos del buffer interno del i2c que es donde llega lo que capta el micrófono.
    n_muestras_capturar = duration * sample_rate
    n_bytes_leidos = 0
    n_muestras_leidas = 0
    #ibuf es el buffer interno, está en bytes.
    #buffer(palabra fancy para decir que es un espacio reservado en memoria "RAM")
    #en esta tarea tenemos dos buffers. 1 - buffer interno (ibuf) el que estamos definiendo al crear el objeto
    #de la clase I2C. 2 - buffer de procesamiento.
    #mode: .RX quiere decir que el ESP32 recibe muestras del micrófono. Si fuera .TX al revés
    #bits: número de bits por muestra.
    
    # descarta los primeros instantes (ruido)
    time.sleep(1)

    print("==========  COMENZANDO GRABACIÓN ==========")
    # bucle de lectura y procesado
    
    while True:
        t0 = time.ticks_us()
        n_bytes_leidos = i2s.readinto(process_buf) # This returns the number of bytes that were read, and write those bytes in the process_buf. So our samples are in the process_buf
        t1 = time.ticks_us()
        profiler.print_partial(t0, t1)
        #por cada iteración está leyendo 2048 muestras readinto method returns the number of bytes that were read 
        #i2s.readinto está modificando a process_buf, porque copia en él las muestras del buffer interno del i2c, donde llegan las muestras del micrófono.
        #solo las copia, aquí no estamos procesando nada, solo estamos copiendo al process_buf 2048 muestras cada que están listas
        #y en la próxima iteración reemplaza las 2048 muestras que copió por las que copiará ahora. 
        n_muestras_leidas += (n_bytes_leidos // 4)
        buffer += process_buf #Estamos concatenando los bytearrays.
        #print("printing bytes")
        for byte in range(16):
            print(f"Byte {byte}: {process_buf[byte]}", end=" ")
            #(Cada 4 bytes(32 bits, size de cada muestra),leemos una sample, el primer byte que se lee de izquierda a derecha(asi por little endian)es el relleno de 8 bits para completar los 32)
        print()
        
        if n_muestras_capturar <= n_muestras_leidas:
            break
    profiler.print_average()
    numpy_buffer = utils.from_int32_buffer(buffer) #This function returns a numpy 1array that put together 32 bits, how? unifying the bits that are back-to-back reading left-to-right.
    #As a result of this we get a buff of lenght 2048, basically, we no longer has our samples divided into 4 bytes but we has them unified, each element of this buff is already a sample.
    
    #ATTENTION:
    #Numpy's arrays has a purpose, something that differentiate them from just normal lists in vanilla python.
    #We can apply element-wise operations. Example: r = [1,2,3,4], then: r * 2 -> [2,4,6,8]. Numpy arrays are basically the same as R vectors. This is a key concept.
    #So, in order to discard 16 bits we just have to take the numpy array and divide it by 2^16.
    """
    You can try this code and confirms everything that was said.
import numpy as np
a = 0b10101010101010101010101
print(bin(a))
print(a)
b = a >> 16 #desplazar 16 bits a la derecha es exactamente igual que simplemente dividir por 2^16.
h = a//2**16
print(len(bin(a)))
print(len(bin(h)))
print(len(bin(b)))
print(bin(h))
print(bin(b))
c = 232
numpy_array = np.array([a, b, c])
print(numpy_array)
print(numpy_array + 4)
    """
    numpy_buffer_16 = np.array((numpy_buffer // 2**16), dtype = np.int16)
    print(len(numpy_buffer_16))
    print("==========  GRABACIÓN FINALIZADA ==========")
    profiler.print_average()
    net.send(numpy_buffer_16)
    net.close()
#


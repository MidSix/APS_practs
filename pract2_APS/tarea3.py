from machine import I2C, Pin
import struct as st
import time

def raw2val(raw_values: bytes, offsets: list = None) -> None:
    sens = 16384
    v_giro = 131
    g = 1
    # H : los interpreta como naturales
    # h : los interpreta como enteros
    # ">H" o ">h" : los interpreta como big endian
    # "<H" o "<H" : los interpreta como little endian
    #">hhhhhhh" o ">7h" es lo mismo. Dos notaciones para referirse a lo mismo.
    #h son dos bytes, por lo que dices que desempaquete 14 bytes del buffer.
    raw_val_pack = st.unpack(">7h", raw_values)
    ax = (raw_val_pack[0] - offsets[0]) / sens * g
    ay = (raw_val_pack[1] - offsets[1]) / sens * g
    az = (raw_val_pack[2] - offsets[2]) / sens * g + 1
    temp = raw_val_pack[3] / 340 + 36.53 # la temperatura no se calibra
    gx = int((raw_val_pack[4] - offsets[4]) / v_giro * g)
    gy = int((raw_val_pack[5] - offsets[5]) / v_giro * g)
    gz = int((raw_val_pack[6] - offsets[6]) / v_giro * g)
        
    print(f" Acel_X: {ax:.2f}g  Acel_Y: {ay:.2f}g  Acel_Z: {az:.2f}g", end=" ")
    print(f" Temp: {temp:} ºC", end=" ")
    print(f" giro_X: {gx}°/s  giro_Y: {gy}°/s  giro_Z: {gz}°/s")
    return raw_val_pack

def trasponer_matriz(matriz: list[list]) -> list:
    new_matriz = []
    for i in range(len(matriz[0])):
        new_matriz.append([fila[i] for fila in matriz])#list comprehension
        #the in-line loop returns a generator object which is also an iterator and then you passes it as an argument
        #to the list function which do all the iterations of the generator and storage all the elements in memory
    return new_matriz

def calibracion(raw_values: list[list]) -> list:
    n_muestras = len(raw_values)
    media = []
    matriz_traspuesta = trasponer_matriz(raw_values)
    for fila in matriz_traspuesta:
        element = 0
        for columna in fila:
            element += columna
        avg = element / n_muestras
        media.append(avg)
    return media

i2c = I2C(0, scl=Pin(19), sda=Pin(18))
device = i2c.scan()
array_bytes = bytearray([0x01])
i2c.writeto_mem(device[0], 0x6b, array_bytes)
captura = []
offsets = None

while True:
    #No hace falta usar bytearray ni struct.pack porque el MPU6050 ya estructura los datos que devuelve
    #bytearray convierte el objeto raw en mutable, esto permite modificar el orden de los bytes si lo necesitas
    #Pero no lo necesitamos, así que no es necesario usarlo en principio.
    #el método readfrom_mem devuelve un objeto tipo bytes que es inmutable. Ya esto es un buffer.
    raw = i2c.readfrom_mem(device[0], 0x3b, 14)
    valores = st.unpack(">7h", raw)
    captura.append(list(valores))
    
    if len(captura) == 50:
        offsets = calibracion(captura)
#     Nada, simplemente para esperar tener las 50 muestras(y hacer  la media para calcular el offset) y con eso poder mostrar los valores ya calibrados
    if offsets is not None:
        raw2val(raw, offsets)
    time.sleep(0.1)

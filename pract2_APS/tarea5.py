from machine import I2C, Pin
import struct as st
import time

def raw2val(raw_values: bytes, offsets: list = None) -> None:
    #register 59, 67
    sens = 32767 # +-32767
    g = 4 # +-4g
    °_s = 1000 # +-1000°_s
    # H : los interpreta como naturales
    # h : los interpreta como enteros
    # ">H" o ">h" : los interpreta como big endian
    # "<H" o "<H" : los interpreta como little endian
    #">hhhhhhh" o ">7h" es lo mismo. Dos notaciones para referirse a lo mismo.
    #h son dos bytes, por lo que dices que desempaquete 14 bytes del buffer.
    raw_val_pack = st.unpack(">7h", raw_values)
    ax = (raw_val_pack[0] - offsets[0]) / (sens / g)
    ay = (raw_val_pack[1] - offsets[1]) / (sens / g)
    az = (raw_val_pack[2] - offsets[2]) / (sens / g) + 1
    temp = raw_val_pack[3] / 340 + 36.53 # la temperatura no se calibra
    gx = int((raw_val_pack[4] - offsets[4]) / (sens / °_s))
    gy = int((raw_val_pack[5] - offsets[5]) / (sens / °_s))
    gz = int((raw_val_pack[6] - offsets[6]) / (sens / °_s))
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
        suma = 0
        for element in fila:
            suma += element
        avg = suma / n_muestras
        media.append(avg)
    return media

def change_scale_config(register: int, s_sel: int):
    """
    It changes the accel or gyro medition scale of the MPU6050.

    Parameters
    ----------
    register: int
        takes the register number

    s_sel: int
        (scale selection) takes a value between 0 - 3 to stablish a valid scale for accel or gyro config
    """

    if s_sel not in list(range(0, 4)):
        raise ValueError("Scale selection (s_sel) take values from 0 through 3 only, please, write one of those values")

    if register not in [27,28]: #0x1b, 0x1c
        raise ValueError("register direction must be the one for GYRO_CONFIG(27) or ACCEL_CONFIG(28) only.")

    s_actual = int(i2c.readfrom_mem(device[0], register, 1)[0])

    #"~", "<<", "&", "|", ">>" Bitwise operators
    # Clear bits 3 and 4 (positions 3 and 4)
    mask_clear = ~(3 << 3)
    s_new = s_actual & mask_clear

    # Set new scale value in bits 3 and 4
    mask_add_bit_3_4 = s_sel << 3
    s_new = s_new | mask_add_bit_3_4

    i2c.writeto_mem(device[0], register, bytearray([s_new]))


def interruption_handler(pin: PIN):
    global new_sample
    new_sample = True

i2c = I2C(0, scl=Pin(19), sda=Pin(18))

pin_for_INT = Pin(12, Pin.IN)

device = i2c.scan()
array_bytes = bytearray([0x01])
i2c.writeto_mem(device[0], 0x6b, array_bytes)

change_scale_config(27, 2) #change the scale of register 27 [gyroconfig]
change_scale_config(28, 1) #change the scale of register 28 [accelconfig]

#Just prints to be sure that the function works correctly
#print(i2c.readfrom_mem(device[0], 27, 1))
#print(i2c.readfrom_mem(device[0], 28, 1))

#Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV). Pag 12 register-map
#where Gyroscope Output Rate = 8kHz when the DLPF is disabled (DLPF_CFG = 0 or 7), and 1kHz
#when the DLPF is enabled.
#Note: The accelerometer output rate is 1kHz.

#So, we are going to see the status of the DLPF(inside the register 26 CONFIG) to know the Output rate of the gyroscope.

#To change gyroscope sample rate
register26 = i2c.readfrom_mem(device[0], 26, 1)
register26 = register26 | (1 << 0) #Se puede poner simplemente uno en lugar de decir que el uno lo mueves 0 bits a la izquierda, lo dejo así solo para acostumbrarse a la sintaxis
i2c.writeto_mem(device[0], 26, bytearray([register26]))

#wanted_sample_rate:
i2c.writeto_mem(device[0], 26, bytearray([1]))

sample_rate = 20
if int(i2c.readfrom_mem(device[0], 26, 1)[0]) in [0, 7]:
    DLPF_disabled = True #Si es true sample_rate de gyroscopioes 8khz
else:
    DLPF_disabled = False

#To change the sample rate
if DLPF_disabled:
    smplrt_div = 8000 // sample_rate - 1 #Gyroscope Output Rate / sample_rate - 1.
    i2c.writeto_mem(device[0], 25, bytearray([(smplrt_div)]))
else:
    smplrt_div = 1000 // sample_rate - 1
    i2c.writeto_mem(device[0], 25, bytearray([smplrt_div]))

#To abilitate the data_ready_interruption of register 56:

#We can't write the number straightforward because what writeto_mem does is to replace the entire register with the value
#you wan't to put in, in other words, it replaces all the bits and we only want to replace the first bit.
#So we have to use a mask:

register56 = int(i2c.readfrom_mem(device[0], 56, 1)[0])
#this is for abilitating it, so I think we can assume that is desactivated: bit0 = 0
register56 = register56 | 1
i2c.writeto_mem(device[0], 56, bytearray([register56]))


captura = []
offsets = None
new_sample = False
pin_for_INT.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=interruption_handler)

#Nada, simplemente para esperar tener las 50 muestras(y hacer  la media para calcular el offset) y con eso poder mostrar los valores ya calibrados
for _ in range(0, 51):
    raw = i2c.readfrom_mem(device[0], 0x3b, 14)
    valores = st.unpack(">7h", raw)
    captura.append(list(valores))
    if len(captura) == 50:
        offsets = calibracion(captura)
while True:
    v = new_sample
    if not v and v:
        print('Esto es imposible')
        break
    if new_sample:
        raw = i2c.readfrom_mem(device[0], 0x3b, 14)
        raw2val(raw, offsets)
        new_sample = False

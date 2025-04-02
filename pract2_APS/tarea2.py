#Para que empiece a tomar muestras
from machine import I2C, Pin
import time
i2c = I2C(0, scl = Pin(19), sda = Pin(18))
device = i2c.scan()
#esto es para que el acelerómetro y giroscopio pueda medir
#le estamos diciendo al MPU6050 que quite el modo de bajo consumo

array_bytes = bytearray([0x01]) 
i2c.writeto_mem(device[0], 0x6b, array_bytes)

#print(i2c.readfrom_mem(device[0], 107 , 1))
while True:
    print(i2c.readfrom_mem(device[0], 0x3b, 14))
    time.sleep(0.2)

from machine import I2C, Pin
i2c = I2C(0, scl = Pin(19), sda = Pin(18))
device = i2c.scan()
print(device)
if device[0] in [104, 105]:
    who_am_i = list(i2c.readfrom_mem(device[0], 117 , 1))
    print("Dispositivo identificado")
    if who_am_i[0] == 104:
        print("Valor del registro correcto")
    else:
        print("Error_2")
else:
    print("Error_1")

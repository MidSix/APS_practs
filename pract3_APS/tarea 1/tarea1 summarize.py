"""
This shit is so damn confuse, so it's better to literally explain in a simple picture first what is happening in each task.
Task 1:
1.-We want to record sound.
2.-We record sounds using a digital microphone(INMP441) that is connected to the ESP32 via wires that are plugged in the motherboard
3.-Samples are sent via I2S(wires) from the microphone to the ESP32(these samples that the microphone returns are already digital(bits) because the microphone has an ADC(Analog to digital converter) integrated, that's why is a "digital" microphone)
4.-Samples get read and processed in the ESP32
5.-Both ESP32 and our computer must be connected to the same wifi network. Because Wifi is the way in which the samples from the ESP32 are sent to the PC
6.-Samples get sent to the pc using WIFI
"""

